import logging

from config.constants import (
    DEFAULT_PRIORITY, STATUS_CANCELLED, STATUS_DONE, STATUS_IN_PROGRESS, STATUS_PENDING,
)
from models.task import Task
from services import validation
from utils.clock import utc_now
from utils.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)

TASK_NOT_FOUND = 'Task não encontrada'


class TaskService:
    def __init__(self, task_repository, user_repository, category_repository):
        self.tasks = task_repository
        self.users = user_repository
        self.categories = category_repository

    def list_tasks(self):
        return self.tasks.list_all_with_relations()

    def get_task(self, task_id):
        task = self.tasks.get(task_id)
        if not task:
            raise NotFoundError(TASK_NOT_FOUND)
        return task

    def create_task(self, data):
        data = validation.ensure_payload(data)

        title = data.get('title')
        if not title:
            raise ValidationError('Título é obrigatório')
        validation.ensure_title(title)

        status = validation.ensure_status(data.get('status', STATUS_PENDING))
        priority = validation.ensure_priority(data.get('priority', DEFAULT_PRIORITY))
        user_id = data.get('user_id')
        category_id = data.get('category_id')
        self._ensure_user_exists(user_id)
        self._ensure_category_exists(category_id)

        task = Task(
            title=title,
            description=data.get('description', ''),
            status=status,
            priority=priority,
            user_id=user_id,
            category_id=category_id,
        )
        if data.get('due_date'):
            task.due_date = validation.parse_due_date(
                data['due_date'], 'Formato de data inválido. Use YYYY-MM-DD')
        if data.get('tags'):
            task.tags = validation.normalize_tags(data['tags'])

        self.tasks.add(task)
        self.tasks.commit('Erro ao criar task')
        logger.info('Task criada: %s - %s', task.id, task.title)
        return task

    def update_task(self, task_id, data):
        task = self.get_task(task_id)
        data = validation.ensure_payload(data)

        if 'title' in data:
            task.title = validation.ensure_title(data['title'])
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = validation.ensure_status(data['status'])
        if 'priority' in data:
            task.priority = validation.ensure_priority(data['priority'])
        if 'user_id' in data:
            self._ensure_user_exists(data['user_id'])
            task.user_id = data['user_id']
        if 'category_id' in data:
            self._ensure_category_exists(data['category_id'])
            task.category_id = data['category_id']
        if 'due_date' in data:
            task.due_date = (
                validation.parse_due_date(data['due_date'], 'Formato de data inválido')
                if data['due_date'] else None
            )
        if 'tags' in data:
            task.tags = validation.normalize_tags(data['tags'])

        task.updated_at = utc_now()
        self.tasks.commit('Erro ao atualizar')
        logger.info('Task atualizada: %s', task.id)
        return task

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        self.tasks.delete(task)
        self.tasks.commit('Erro ao deletar')
        logger.info('Task deletada: %s', task_id)

    def search(self, text, status, priority, user_id):
        priority = validation.parse_int_param(priority, 'priority') if priority else None
        user_id = validation.parse_int_param(user_id, 'user_id') if user_id else None
        return self.tasks.search(text, status, priority, user_id)

    def stats(self):
        total = self.tasks.count()
        by_status = self.tasks.count_by_status()
        done = by_status.get(STATUS_DONE, 0)
        return {
            'total': total,
            'pending': by_status.get(STATUS_PENDING, 0),
            'in_progress': by_status.get(STATUS_IN_PROGRESS, 0),
            'done': done,
            'cancelled': by_status.get(STATUS_CANCELLED, 0),
            'overdue': len(self.tasks.overdue(utc_now())),
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }

    def _ensure_user_exists(self, user_id):
        if user_id and not self.users.get(user_id):
            raise NotFoundError('Usuário não encontrado')

    def _ensure_category_exists(self, category_id):
        if category_id and not self.categories.get(category_id):
            raise NotFoundError('Categoria não encontrada')
