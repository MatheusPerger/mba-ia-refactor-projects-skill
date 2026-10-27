from models.produto import Produto


class ProdutoRepository:
    def __init__(self, db):
        self._db = db

    def listar(self):
        rows = self._db.connection().execute("SELECT * FROM produtos").fetchall()
        return [Produto.from_row(row) for row in rows]

    def buscar_por_id(self, produto_id):
        row = self._db.connection().execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return Produto.from_row(row) if row else None

    def buscar_por_ids(self, ids):
        if not ids:
            return {}
        marcas = ",".join("?" * len(ids))
        rows = self._db.connection().execute(f"SELECT * FROM produtos WHERE id IN ({marcas})", list(ids)).fetchall()
        return {row["id"]: Produto.from_row(row) for row in rows}

    def pesquisar(self, termo, categoria, preco_min, preco_max):
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max:
            query += " AND preco <= ?"
            params.append(preco_max)
        rows = self._db.connection().execute(query, params).fetchall()
        return [Produto.from_row(row) for row in rows]

    def criar(self, nome, descricao, preco, estoque, categoria):
        cursor = self._db.connection().execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        return cursor.lastrowid

    def atualizar(self, produto_id, nome, descricao, preco, estoque, categoria):
        self._db.connection().execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )

    def deletar(self, produto_id):
        self._db.connection().execute("DELETE FROM produtos WHERE id = ?", (produto_id,))

    def baixar_estoque(self, produto_id, quantidade):
        """Baixa o estoque só se houver quantidade suficiente. Retorna False se não houver."""
        cursor = self._db.connection().execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
            (quantidade, produto_id, quantidade),
        )
        return cursor.rowcount == 1

    def contar(self):
        return self._db.connection().execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
