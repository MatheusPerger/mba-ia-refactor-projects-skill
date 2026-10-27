from flask import jsonify, request

from views.task_view import task_detail, task_list_item, task_to_dict


class TaskController:
    def __init__(self, task_service):
        self.service = task_service

    def list_tasks(self):
        return jsonify([task_list_item(task) for task in self.service.list_tasks()]), 200

    def get_task(self, task_id):
        return jsonify(task_detail(self.service.get_task(task_id))), 200

    def create_task(self):
        task = self.service.create_task(request.get_json())
        return jsonify(task_to_dict(task)), 201

    def update_task(self, task_id):
        task = self.service.update_task(task_id, request.get_json())
        return jsonify(task_to_dict(task)), 200

    def delete_task(self, task_id):
        self.service.delete_task(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200

    def search_tasks(self):
        tasks = self.service.search(
            request.args.get('q', ''),
            request.args.get('status', ''),
            request.args.get('priority', ''),
            request.args.get('user_id', ''),
        )
        return jsonify([task_to_dict(task) for task in tasks]), 200

    def stats(self):
        return jsonify(self.service.stats()), 200
