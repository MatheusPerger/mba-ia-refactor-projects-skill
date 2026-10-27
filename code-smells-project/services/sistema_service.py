import logging

logger = logging.getLogger(__name__)


class SistemaService:
    def __init__(self, db, sistema_repository, produto_repository, usuario_repository, pedido_repository):
        self._db = db
        self._sistema = sistema_repository
        self._produtos = produto_repository
        self._usuarios = usuario_repository
        self._pedidos = pedido_repository

    def resetar_banco(self):
        try:
            self._sistema.limpar_tabelas()
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise
        logger.warning("Banco de dados resetado")

    def status(self):
        self._sistema.testar_conexao()
        return {
            "produtos": self._produtos.contar(),
            "usuarios": self._usuarios.contar(),
            "pedidos": self._pedidos.contar(),
        }
