import logging

from config.constants import (
    STATUS_APROVADO, STATUS_CANCELADO, STATUS_PEDIDO_VALIDOS, STATUS_PENDENTE, TIPO_ADMIN,
)
from services.errors import ForbiddenError, ValidationError

logger = logging.getLogger(__name__)


def _inteiro_positivo(valor):
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


class PedidoService:
    def __init__(self, db, pedido_repository, produto_repository):
        self._db = db
        self._pedidos = pedido_repository
        self._produtos = produto_repository

    def criar(self, usuario_id, itens, solicitante):
        if not usuario_id:
            raise ValidationError("Usuario ID é obrigatório")
        if solicitante["tipo"] != TIPO_ADMIN and str(solicitante["id"]) != str(usuario_id):
            raise ForbiddenError("Sem permissão para criar pedido de outro usuário")
        if not itens or not isinstance(itens, list):
            raise ValidationError("Pedido deve ter pelo menos 1 item")
        for item in itens:
            if not isinstance(item, dict) or not _inteiro_positivo(item.get("produto_id")) \
                    or not _inteiro_positivo(item.get("quantidade")):
                raise ValidationError("Cada item deve ter produto_id e quantidade inteiros e positivos")

        produtos = self._produtos.buscar_por_ids({item["produto_id"] for item in itens})
        total = 0
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                raise ValidationError(f"Produto {item['produto_id']} não encontrado", sucesso=False)
            if produto.estoque < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {produto.nome}", sucesso=False)
            total += produto.preco * item["quantidade"]

        try:
            pedido_id = self._pedidos.criar(usuario_id, STATUS_PENDENTE, total)
            for item in itens:
                produto = produtos[item["produto_id"]]
                self._pedidos.adicionar_item(pedido_id, produto.id, item["quantidade"], produto.preco)
                if not self._produtos.baixar_estoque(produto.id, item["quantidade"]):
                    raise ValidationError(f"Estoque insuficiente para {produto.nome}", sucesso=False)
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

        logger.info("EMAIL: pedido %s criado para usuario %s", pedido_id, usuario_id)
        logger.info("SMS: pedido %s recebido", pedido_id)
        logger.info("PUSH: novo pedido %s recebido pelo sistema", pedido_id)
        return {"pedido_id": pedido_id, "total": total}

    def listar_todos(self):
        return self._pedidos.listar_todos()

    def listar_por_usuario(self, usuario_id):
        return self._pedidos.listar_por_usuario(usuario_id)

    def atualizar_status(self, pedido_id, novo_status):
        if novo_status not in STATUS_PEDIDO_VALIDOS:
            raise ValidationError("Status inválido")
        self._pedidos.atualizar_status(pedido_id, novo_status)
        self._db.commit()

        if novo_status == STATUS_APROVADO:
            logger.info("NOTIFICAÇÃO: pedido %s aprovado. Preparar envio.", pedido_id)
        if novo_status == STATUS_CANCELADO:
            logger.info("NOTIFICAÇÃO: pedido %s cancelado. Devolver estoque.", pedido_id)
