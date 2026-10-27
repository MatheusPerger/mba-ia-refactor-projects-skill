import logging
import sqlite3

from flask import g
from werkzeug.security import generate_password_hash

from config import settings
from config.constants import TIPO_ADMIN, TIPO_CLIENTE

logger = logging.getLogger(__name__)

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    )
    """,
]

PRODUTOS_SEED = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

USUARIOS_SEED = [
    ("Admin", "admin@loja.com", "admin123", TIPO_ADMIN),
    ("João Silva", "joao@email.com", "123456", TIPO_CLIENTE),
    ("Maria Santos", "maria@email.com", "senha123", TIPO_CLIENTE),
]


class Database:
    """Conexão SQLite por requisição (via flask.g). Schema e seed rodam uma vez, em init()."""

    def connection(self):
        if "db" not in g:
            g.db = sqlite3.connect(settings.DATABASE_PATH)
            g.db.row_factory = sqlite3.Row
        return g.db

    def commit(self):
        self.connection().commit()

    def rollback(self):
        self.connection().rollback()

    def close(self, _erro=None):
        conexao = g.pop("db", None)
        if conexao is not None:
            conexao.close()

    def init(self):
        conexao = sqlite3.connect(settings.DATABASE_PATH)
        try:
            for ddl in SCHEMA:
                conexao.execute(ddl)
            if conexao.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
                conexao.executemany(
                    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                    PRODUTOS_SEED,
                )
                conexao.executemany(
                    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                    [(nome, email, generate_password_hash(senha), tipo) for nome, email, senha, tipo in USUARIOS_SEED],
                )
                logger.info("Banco inicializado com dados de exemplo")
            conexao.commit()
        finally:
            conexao.close()
