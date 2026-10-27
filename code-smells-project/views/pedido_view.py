def serializar_pedido(pedido):
    return {
        "id": pedido.id,
        "usuario_id": pedido.usuario_id,
        "status": pedido.status,
        "total": pedido.total,
        "criado_em": pedido.criado_em,
        "itens": [
            {
                "produto_id": item.produto_id,
                "produto_nome": item.produto_nome,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario,
            }
            for item in pedido.itens
        ],
    }


def serializar_pedidos(pedidos):
    return [serializar_pedido(pedido) for pedido in pedidos]
