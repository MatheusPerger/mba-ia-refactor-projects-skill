from dataclasses import dataclass


@dataclass
class Produto:
    id: int
    nome: str
    descricao: str
    preco: float
    estoque: int
    categoria: str
    ativo: int
    criado_em: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            nome=row["nome"],
            descricao=row["descricao"],
            preco=row["preco"],
            estoque=row["estoque"],
            categoria=row["categoria"],
            ativo=row["ativo"],
            criado_em=row["criado_em"],
        )
