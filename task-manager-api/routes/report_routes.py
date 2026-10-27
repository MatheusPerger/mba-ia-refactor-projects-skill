from flask import Blueprint


def create_report_blueprint(controller, auth):
    bp = Blueprint('reports', __name__)
    bp.add_url_rule('/reports/summary', view_func=auth.admin_required(controller.summary), methods=['GET'])
    bp.add_url_rule('/reports/user/<int:user_id>', view_func=auth.admin_required(controller.user_report), methods=['GET'])
    return bp
