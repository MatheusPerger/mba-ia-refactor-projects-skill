from models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db):
        self._db = db

    def listar(self):
        rows = self._db.connection().execute("SELECT * FROM usuarios").fetchall()
        return [Usuario.from_row(row) for row in rows]

    def buscar_por_id(self, usuario_id):
        row = self._db.connection().execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        return Usuario.from_row(row) if row else None

    def buscar_por_email(self, email):
        rows = self._db.connection().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchall()
        return [Usuario.from_row(row) for row in rows]

    def criar(self, nome, email, senha_hash, tipo):
        cursor = self._db.connection().execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_hash, tipo),
        )
        return cursor.lastrowid

    def atualizar_senha(self, usuario_id, senha_hash):
        self._db.connection().execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id))

    def contar(self):
        return self._db.connection().execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
