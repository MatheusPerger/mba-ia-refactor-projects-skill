import logging

from config.constants import ROLE_USER
from models.user import User
from services import validation
from utils.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)

USER_NOT_FOUND = 'Usuário não encontrado'


class UserService:
    def __init__(self, user_repository, task_repository):
        self.users = user_repository
        self.tasks = task_repository

    def list_users(self):
        counts = self.tasks.count_by_user()
        return [(user, counts.get(user.id, 0)) for user in self.users.list_all()]

    def get_user(self, user_id):
        user = self.users.get(user_id)
        if not user:
            raise NotFoundError(USER_NOT_FOUND)
        return user

    def get_user_with_tasks(self, user_id):
        user = self.get_user(user_id)
        return user, self.tasks.list_by_user(user_id)

    def list_user_tasks(self, user_id):
        self.get_user(user_id)
        return self.tasks.list_by_user(user_id)

    def create_user(self, data, requested_by_admin=False):
        data = validation.ensure_payload(data)
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', ROLE_USER)

        if not name:
            raise ValidationError('Nome é obrigatório')
        if not email:
            raise ValidationError('Email é obrigatório')
        if not password:
            raise ValidationError('Senha é obrigatória')
        validation.ensure_email(email)
        validation.ensure_password(password, 'Senha deve ter no mínimo 4 caracteres')
        if self.users.get_by_email(email):
            raise ConflictError('Email já cadastrado')
        validation.ensure_role(role)

        user = User(name=name, email=email, role=role if requested_by_admin else ROLE_USER)
        user.set_password(password)
        self.users.add(user)
        self.users.commit('Erro ao criar usuário')
        logger.info('Usuário criado: %s - %s', user.id, user.name)
        return user

    def update_user(self, user_id, data, acting_user):
        user = self.get_user(user_id)
        data = validation.ensure_payload(data)

        if not acting_user.is_admin():
            if acting_user.id != user.id or 'role' in data or 'active' in data:
                raise ForbiddenError()

        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            validation.ensure_email(data['email'])
            existing = self.users.get_by_email(data['email'])
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = data['email']
        if 'password' in data:
            validation.ensure_password(data['password'], 'Senha muito curta')
            user.set_password(data['password'])
        if 'role' in data:
            user.role = validation.ensure_role(data['role'])
        if 'active' in data:
            if not isinstance(data['active'], bool):
                raise ValidationError('Active inválido')
            user.active = data['active']

        self.users.commit('Erro ao atualizar')
        return user

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        for task in self.tasks.list_by_user(user_id):
            self.tasks.delete(task)
        self.users.delete(user)
        self.users.commit('Erro ao deletar')
        logger.info('Usuário deletado: %s', user_id)
