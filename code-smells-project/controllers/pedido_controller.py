from flask import g, jsonify, request

from services.errors import ValidationError
from views.pedido_view import serializar_pedidos


class PedidoController:
    def __init__(self, pedido_service):
        self._service = pedido_service

    def criar(self):
        dados = request.get_json(silent=True)
        if not dados or not isinstance(dados, dict):
            raise ValidationError("Dados inválidos")
        resultado = self._service.criar(dados.get("usuario_id"), dados.get("itens", []), g.usuario_atual)
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201

    def listar_todos(self):
        return jsonify({"dados": serializar_pedidos(self._service.listar_todos()), "sucesso": True}), 200

    def listar_por_usuario(self, usuario_id):
        pedidos = self._service.listar_por_usuario(usuario_id)
        return jsonify({"dados": serializar_pedidos(pedidos), "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        dados = request.get_json(silent=True)
        novo_status = dados.get("status", "") if isinstance(dados, dict) else ""
        self._service.atualizar_status(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
