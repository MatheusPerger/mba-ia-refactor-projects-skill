from config.constants import FAIXAS_DESCONTO, STATUS_APROVADO, STATUS_CANCELADO, STATUS_PENDENTE


def _calcular_desconto(faturamento):
    for limite, percentual in FAIXAS_DESCONTO:
        if faturamento > limite:
            return faturamento * percentual
    return 0


class RelatorioService:
    def __init__(self, pedido_repository):
        self._pedidos = pedido_repository

    def vendas(self):
        total_pedidos = self._pedidos.contar()
        faturamento = self._pedidos.somar_total() or 0
        desconto = _calcular_desconto(faturamento)
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": self._pedidos.contar(STATUS_PENDENTE),
            "pedidos_aprovados": self._pedidos.contar(STATUS_APROVADO),
            "pedidos_cancelados": self._pedidos.contar(STATUS_CANCELADO),
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
        }
