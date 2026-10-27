class AppError(Exception):
    """Erro de domínio. O middleware de erros converte em resposta HTTP padronizada."""

    status = 500

    def __init__(self, mensagem, sucesso=None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.sucesso = sucesso


class ValidationError(AppError):
    status = 400


class AuthenticationError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403


class NotFoundError(AppError):
    status = 404
