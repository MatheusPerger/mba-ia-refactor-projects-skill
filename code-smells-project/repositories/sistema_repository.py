TABELAS_PARA_LIMPAR = ["itens_pedido", "pedidos", "produtos", "usuarios"]


class SistemaRepository:
    def __init__(self, db):
        self._db = db

    def limpar_tabelas(self):
        conexao = self._db.connection()
        for tabela in TABELAS_PARA_LIMPAR:
            conexao.execute(f"DELETE FROM {tabela}")

    def testar_conexao(self):
        self._db.connection().execute("SELECT 1")
