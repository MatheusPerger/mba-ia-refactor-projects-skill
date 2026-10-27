from flask import jsonify, request

from views.category_view import category_list_item, category_to_dict


class CategoryController:
    def __init__(self, category_service):
        self.service = category_service

    def list_categories(self):
        categories = self.service.list_categories()
        return jsonify([category_list_item(category, count) for category, count in categories]), 200

    def create_category(self):
        category = self.service.create_category(request.get_json())
        return jsonify(category_to_dict(category)), 201

    def update_category(self, cat_id):
        category = self.service.update_category(cat_id, request.get_json())
        return jsonify(category_to_dict(category)), 200

    def delete_category(self, cat_id):
        self.service.delete_category(cat_id)
        return jsonify({'message': 'Categoria deletada'}), 200
