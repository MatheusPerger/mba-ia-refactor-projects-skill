def serializar_produto(produto):
    return {
        "id": produto.id,
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco": produto.preco,
        "estoque": produto.estoque,
        "categoria": produto.categoria,
        "ativo": produto.ativo,
        "criado_em": produto.criado_em,
    }


def serializar_produtos(produtos):
    return [serializar_produto(produto) for produto in produtos]
