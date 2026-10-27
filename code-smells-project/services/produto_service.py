import logging

from config.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from services.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


def _eh_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_produto(dados):
    if not dados or not isinstance(dados, dict):
        raise ValidationError("Dados inválidos")
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome deve ser texto")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição deve ser texto")
    if not _eh_numero(preco):
        raise ValidationError("Preço deve ser numérico")
    if not isinstance(estoque, int) or isinstance(estoque, bool):
        raise ValidationError("Estoque deve ser um número inteiro")
    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return nome, descricao, preco, estoque, categoria


def _validar_numero_filtro(valor, nome_filtro):
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        raise ValidationError(f"{nome_filtro} deve ser numérico")


class ProdutoService:
    def __init__(self, db, produto_repository):
        self._db = db
        self._produtos = produto_repository

    def listar(self):
        produtos = self._produtos.listar()
        logger.info("Listando %d produtos", len(produtos))
        return produtos

    def buscar(self, produto_id):
        produto = self._produtos.buscar_por_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado", sucesso=False)
        return produto

    def pesquisar(self, termo, categoria, preco_min, preco_max):
        preco_min = _validar_numero_filtro(preco_min, "preco_min")
        preco_max = _validar_numero_filtro(preco_max, "preco_max")
        return self._produtos.pesquisar(termo, categoria, preco_min, preco_max)

    def criar(self, dados):
        campos = _validar_produto(dados)
        produto_id = self._produtos.criar(*campos)
        self._db.commit()
        logger.info("Produto criado com ID: %s", produto_id)
        return produto_id

    def atualizar(self, produto_id, dados):
        if not self._produtos.buscar_por_id(produto_id):
            raise NotFoundError("Produto não encontrado")
        campos = _validar_produto(dados)
        self._produtos.atualizar(produto_id, *campos)
        self._db.commit()

    def deletar(self, produto_id):
        if not self._produtos.buscar_por_id(produto_id):
            raise NotFoundError("Produto não encontrado")
        self._produtos.deletar(produto_id)
        self._db.commit()
        logger.info("Produto %s deletado", produto_id)
