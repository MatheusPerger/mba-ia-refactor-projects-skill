from flask import jsonify

from config import settings
from config.constants import APP_VERSION


class SistemaController:
    def __init__(self, sistema_service):
        self._service = sistema_service

    def index(self):
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": APP_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    def health(self):
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": self._service.status(),
            "versao": APP_VERSION,
            "ambiente": settings.AMBIENTE,
        }), 200

    def resetar_banco(self):
        self._service.resetar_banco()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
