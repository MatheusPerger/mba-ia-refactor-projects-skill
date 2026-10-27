from dataclasses import dataclass, field
from typing import List


@dataclass
class ItemPedido:
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float


@dataclass
class Pedido:
    id: int
    usuario_id: int
    status: str
    total: float
    criado_em: str
    itens: List[ItemPedido] = field(default_factory=list)

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            usuario_id=row["usuario_id"],
            status=row["status"],
            total=row["total"],
            criado_em=row["criado_em"],
        )
