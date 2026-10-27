from functools import wraps

from flask import g, request

from utils.errors import ForbiddenError, UnauthorizedError

BEARER_PREFIX = 'Bearer '


class AuthMiddleware:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def _token(self):
        header = request.headers.get('Authorization', '')
        return header[len(BEARER_PREFIX):] if header.startswith(BEARER_PREFIX) else None

    def optional_user(self):
        token = self._token()
        return self.auth_service.user_from_token(token) if token else None

    def login_required(self, view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = self.optional_user()
            if not user:
                raise UnauthorizedError()
            g.current_user = user
            return view(*args, **kwargs)
        return wrapper

    def admin_required(self, view):
        @wraps(view)
        @self.login_required
        def wrapper(*args, **kwargs):
            if not g.current_user.is_admin():
                raise ForbiddenError()
            return view(*args, **kwargs)
        return wrapper
