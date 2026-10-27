class AppError(Exception):
    status_code = 500
    message = 'Erro interno'

    def __init__(self, message=None):
        super().__init__(message or self.message)
        self.message = message or self.message


class ValidationError(AppError):
    status_code = 400
    message = 'Dados inválidos'


class UnauthorizedError(AppError):
    status_code = 401
    message = 'Não autenticado'


class ForbiddenError(AppError):
    status_code = 403
    message = 'Sem permissão'


class NotFoundError(AppError):
    status_code = 404
    message = 'Não encontrado'


class ConflictError(AppError):
    status_code = 409
    message = 'Conflito'


class PersistenceError(AppError):
    status_code = 500
    message = 'Erro ao gravar dados'
