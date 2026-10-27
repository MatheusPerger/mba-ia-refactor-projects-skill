from config.constants import DEFAULT_COLOR
from models.category import Category
from services import validation
from utils.errors import NotFoundError, ValidationError

CATEGORY_NOT_FOUND = 'Categoria não encontrada'


class CategoryService:
    def __init__(self, category_repository, task_repository):
        self.categories = category_repository
        self.tasks = task_repository

    def list_categories(self):
        counts = self.tasks.count_by_category()
        return [(category, counts.get(category.id, 0)) for category in self.categories.list_all()]

    def create_category(self, data):
        data = validation.ensure_payload(data)
        name = data.get('name')
        if not name:
            raise ValidationError('Nome é obrigatório')

        category = Category(
            name=name,
            description=data.get('description', ''),
            color=data.get('color', DEFAULT_COLOR),
        )
        self.categories.add(category)
        self.categories.commit('Erro ao criar categoria')
        return category

    def update_category(self, category_id, data):
        category = self._get(category_id)
        data = validation.ensure_payload(data)
        for field in ('name', 'description', 'color'):
            if field in data:
                setattr(category, field, data[field])
        self.categories.commit('Erro ao atualizar')
        return category

    def delete_category(self, category_id):
        category = self._get(category_id)
        self.categories.delete(category)
        self.categories.commit('Erro ao deletar')

    def _get(self, category_id):
        category = self.categories.get(category_id)
        if not category:
            raise NotFoundError(CATEGORY_NOT_FOUND)
        return category
