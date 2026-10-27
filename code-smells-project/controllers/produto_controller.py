from flask import jsonify, request

from views.produto_view import serializar_produto, serializar_produtos


class ProdutoController:
    def __init__(self, produto_service):
        self._service = produto_service

    def listar(self):
        return jsonify({"dados": serializar_produtos(self._service.listar()), "sucesso": True}), 200

    def buscar(self, id):
        return jsonify({"dados": serializar_produto(self._service.buscar(id)), "sucesso": True}), 200

    def pesquisar(self, **_):
        resultados = self._service.pesquisar(
            request.args.get("q", ""),
            request.args.get("categoria"),
            request.args.get("preco_min"),
            request.args.get("preco_max"),
        )
        return jsonify({"dados": serializar_produtos(resultados), "total": len(resultados), "sucesso": True}), 200

    def criar(self):
        produto_id = self._service.criar(request.get_json(silent=True))
        return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

    def atualizar(self, id):
        self._service.atualizar(id, request.get_json(silent=True))
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, id):
        self._service.deletar(id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
