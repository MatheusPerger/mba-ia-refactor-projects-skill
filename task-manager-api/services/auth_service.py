import logging

from itsdangerous import BadSignature, URLSafeTimedSerializer

from utils.errors import ForbiddenError, PersistenceError, UnauthorizedError, ValidationError

logger = logging.getLogger(__name__)

TOKEN_SALT = 'task-manager-auth'


class AuthService:
    def __init__(self, user_repository, secret_key, token_max_age):
        self.users = user_repository
        self.serializer = URLSafeTimedSerializer(secret_key, salt=TOKEN_SALT)
        self.token_max_age = token_max_age

    def login(self, data):
        if not data or not isinstance(data, dict):
            raise ValidationError('Dados inválidos')
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            raise ValidationError('Email e senha são obrigatórios')

        user = self.users.get_by_email(email)
        if not user or not user.check_password(password):
            raise UnauthorizedError('Credenciais inválidas')
        if not user.active:
            raise ForbiddenError('Usuário inativo')

        self._upgrade_legacy_hash(user, password)
        return user, self.issue_token(user)

    def issue_token(self, user):
        return self.serializer.dumps({'uid': user.id})

    def user_from_token(self, token):
        """Devolve o usuário ativo dono do token ou None se o token for inválido/expirado."""
        try:
            payload = self.serializer.loads(token, max_age=self.token_max_age)
        except BadSignature:
            return None
        user = self.users.get(payload.get('uid'))
        return user if user and user.active else None

    def _upgrade_legacy_hash(self, user, password):
        if not user.uses_legacy_hash():
            return
        user.set_password(password)
        try:
            self.users.commit('Erro ao atualizar')
        except PersistenceError:
            logger.warning('Não foi possível migrar o hash da senha do usuário %s', user.id)
