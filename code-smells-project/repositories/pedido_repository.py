from models.pedido import ItemPedido, Pedido


class PedidoRepository:
    def __init__(self, db):
        self._db = db

    def criar(self, usuario_id, status, total):
        cursor = self._db.connection().execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, status, total),
        )
        return cursor.lastrowid

    def adicionar_item(self, pedido_id, produto_id, quantidade, preco_unitario):
        self._db.connection().execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario),
        )

    def listar_todos(self):
        rows = self._db.connection().execute("SELECT * FROM pedidos").fetchall()
        return self._com_itens(rows)

    def listar_por_usuario(self, usuario_id):
        rows = self._db.connection().execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)).fetchall()
        return self._com_itens(rows)

    def atualizar_status(self, pedido_id, status):
        self._db.connection().execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))

    def contar(self, status=None):
        if status is None:
            return self._db.connection().execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        return self._db.connection().execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,)).fetchone()[0]

    def somar_total(self):
        return self._db.connection().execute("SELECT SUM(total) FROM pedidos").fetchone()[0]

    def _com_itens(self, rows):
        """Monta os pedidos com seus itens em uma única consulta (evita N+1)."""
        pedidos = {row["id"]: Pedido.from_row(row) for row in rows}
        if not pedidos:
            return []
        marcas = ",".join("?" * len(pedidos))
        itens = self._db.connection().execute(
            "SELECT i.pedido_id, i.produto_id, i.quantidade, i.preco_unitario, p.nome AS produto_nome, "
            "p.id AS produto_existente "
            "FROM itens_pedido i LEFT JOIN produtos p ON p.id = i.produto_id "
            f"WHERE i.pedido_id IN ({marcas}) ORDER BY i.id",
            list(pedidos),
        ).fetchall()
        for item in itens:
            nome = item["produto_nome"] if item["produto_existente"] is not None else "Desconhecido"
            pedidos[item["pedido_id"]].itens.append(
                ItemPedido(item["produto_id"], nome, item["quantidade"], item["preco_unitario"])
            )
        return list(pedidos.values())
