from flask import jsonify, request

from views.usuario_view import serializar_login, serializar_usuario, serializar_usuarios


class UsuarioController:
    def __init__(self, usuario_service):
        self._service = usuario_service

    def listar(self):
        return jsonify({"dados": serializar_usuarios(self._service.listar()), "sucesso": True}), 200

    def buscar(self, id):
        return jsonify({"dados": serializar_usuario(self._service.buscar(id)), "sucesso": True}), 200

    def criar(self):
        usuario_id = self._service.criar(request.get_json(silent=True))
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201

    def login(self):
        usuario, token = self._service.login(request.get_json(silent=True))
        return jsonify({"dados": serializar_login(usuario, token), "sucesso": True, "mensagem": "Login OK"}), 200
