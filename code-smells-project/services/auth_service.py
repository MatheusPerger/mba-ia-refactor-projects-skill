from itsdangerous import BadSignature, URLSafeTimedSerializer

from services.errors import AuthenticationError


class AuthService:
    def __init__(self, secret_key, max_age_segundos):
        self._serializer = URLSafeTimedSerializer(secret_key, salt="auth-token")
        self._max_age = max_age_segundos

    def emitir_token(self, usuario):
        return self._serializer.dumps({"id": usuario.id, "tipo": usuario.tipo})

    def validar_token(self, token):
        try:
            return self._serializer.loads(token, max_age=self._max_age)
        except BadSignature:
            raise AuthenticationError("Token inválido ou expirado")
