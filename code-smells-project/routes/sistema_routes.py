from flask import Blueprint


def criar_blueprint(controller, auth):
    bp = Blueprint("sistema", __name__)
    bp.add_url_rule("/", "index", controller.index, methods=["GET"])
    bp.add_url_rule("/health", "health_check", controller.health, methods=["GET"])
    bp.add_url_rule("/admin/reset-db", "reset_database", auth.admin(controller.resetar_banco), methods=["POST"])
    return bp
