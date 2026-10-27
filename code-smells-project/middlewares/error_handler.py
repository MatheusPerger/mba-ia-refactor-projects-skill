import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from services.errors import AppError

logger = logging.getLogger(__name__)


def registrar_error_handlers(app):
    @app.errorhandler(AppError)
    def tratar_erro_de_dominio(erro):
        corpo = {"erro": erro.mensagem}
        if erro.sucesso is not None:
            corpo["sucesso"] = erro.sucesso
        return jsonify(corpo), erro.status

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro):
        return erro

    @app.errorhandler(Exception)
    def tratar_erro_inesperado(erro):
        logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
