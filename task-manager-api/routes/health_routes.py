from flask import Blueprint

from controllers import health_controller


def create_health_blueprint():
    bp = Blueprint('health', __name__)
    bp.add_url_rule('/health', view_func=health_controller.health)
    bp.add_url_rule('/', view_func=health_controller.index)
    return bp
