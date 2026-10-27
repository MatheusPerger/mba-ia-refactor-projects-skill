from flask import g, jsonify, request

from views.task_view import task_summary, task_to_dict
from views.user_view import user_list_item, user_to_dict


class UserController:
    def __init__(self, user_service, auth_service, auth_middleware):
        self.service = user_service
        self.auth_service = auth_service
        self.auth = auth_middleware

    def list_users(self):
        users = self.service.list_users()
        return jsonify([user_list_item(user, count) for user, count in users]), 200

    def get_user(self, user_id):
        user, tasks = self.service.get_user_with_tasks(user_id)
        return jsonify({**user_to_dict(user), 'tasks': [task_to_dict(task) for task in tasks]}), 200

    def create_user(self):
        acting_user = self.auth.optional_user()
        is_admin = bool(acting_user and acting_user.is_admin())
        user = self.service.create_user(request.get_json(), requested_by_admin=is_admin)
        return jsonify(user_to_dict(user)), 201

    def update_user(self, user_id):
        user = self.service.update_user(user_id, request.get_json(), g.current_user)
        return jsonify(user_to_dict(user)), 200

    def delete_user(self, user_id):
        self.service.delete_user(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200

    def list_user_tasks(self, user_id):
        tasks = self.service.list_user_tasks(user_id)
        return jsonify([task_summary(task) for task in tasks]), 200

    def login(self):
        user, token = self.auth_service.login(request.get_json())
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user_to_dict(user),
            'token': token,
        }), 200
