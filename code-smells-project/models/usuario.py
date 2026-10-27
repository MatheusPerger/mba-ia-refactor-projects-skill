from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    tipo: str
    criado_em: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            nome=row["nome"],
            email=row["email"],
            senha=row["senha"],
            tipo=row["tipo"],
            criado_em=row["criado_em"],
        )
