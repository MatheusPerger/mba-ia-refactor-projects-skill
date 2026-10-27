from flask import Blueprint


def criar_blueprint(controller, auth):
    bp = Blueprint("relatorios", __name__)
    bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", auth.admin(controller.vendas), methods=["GET"])
    return bp
