from functools import wraps

from flask import g, request

from config.constants import TIPO_ADMIN
from services.errors import AuthenticationError, ForbiddenError


class AuthMiddleware:
    def __init__(self, auth_service):
        self._auth = auth_service

    def _identificar(self):
        cabecalho = request.headers.get("Authorization", "")
        if not cabecalho.startswith("Bearer "):
            raise AuthenticationError("Não autenticado")
        g.usuario_atual = self._auth.validar_token(cabecalho[len("Bearer "):])

    def autenticado(self, view):
        @wraps(view)
        def envolvido(*args, **kwargs):
            self._identificar()
            return view(*args, **kwargs)
        return envolvido

    def admin(self, view):
        @wraps(view)
        def envolvido(*args, **kwargs):
            self._identificar()
            if g.usuario_atual["tipo"] != TIPO_ADMIN:
                raise ForbiddenError("Sem permissão")
            return view(*args, **kwargs)
        return envolvido

    def proprio_ou_admin(self, parametro):
        """Permite o acesso ao próprio usuário (id na URL) ou a um admin."""
        def decorador(view):
            @wraps(view)
            def envolvido(*args, **kwargs):
                self._identificar()
                usuario = g.usuario_atual
                if usuario["tipo"] != TIPO_ADMIN and usuario["id"] != kwargs.get(parametro):
                    raise ForbiddenError("Sem permissão")
                return view(*args, **kwargs)
            return envolvido
        return decorador
