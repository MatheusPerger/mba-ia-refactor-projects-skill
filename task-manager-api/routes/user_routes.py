from flask import Blueprint


def create_user_blueprint(controller, auth):
    bp = Blueprint('users', __name__)
    bp.add_url_rule('/users', view_func=controller.list_users, methods=['GET'])
    bp.add_url_rule('/users/<int:user_id>', view_func=controller.get_user, methods=['GET'])
    bp.add_url_rule('/users', view_func=controller.create_user, methods=['POST'])
    bp.add_url_rule('/users/<int:user_id>', view_func=auth.login_required(controller.update_user), methods=['PUT'])
    bp.add_url_rule('/users/<int:user_id>', view_func=auth.admin_required(controller.delete_user), methods=['DELETE'])
    bp.add_url_rule('/users/<int:user_id>/tasks', view_func=controller.list_user_tasks, methods=['GET'])
    bp.add_url_rule('/login', view_func=controller.login, methods=['POST'])
    return bp
