import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from utils.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({'error': err.message}), err.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(err):
        return err

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception('Erro inesperado')
        return jsonify({'error': 'Erro interno'}), 500
