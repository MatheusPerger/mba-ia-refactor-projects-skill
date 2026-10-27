import hmac
import logging

from werkzeug.security import check_password_hash, generate_password_hash

from config.constants import TIPO_CLIENTE
from services.errors import AuthenticationError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)

PREFIXOS_HASH = ("scrypt:", "pbkdf2:")


def _senha_confere(senha_informada, senha_armazenada):
    if senha_armazenada.startswith(PREFIXOS_HASH):
        return check_password_hash(senha_armazenada, senha_informada)
    # senha legada em texto puro: aceita uma última vez e é regravada como hash
    return hmac.compare_digest(senha_armazenada.encode(), senha_informada.encode())


def _campo_texto(dados, campo):
    valor = dados.get(campo, "")
    return valor if isinstance(valor, str) else ""


class UsuarioService:
    def __init__(self, db, usuario_repository, auth_service):
        self._db = db
        self._usuarios = usuario_repository
        self._auth = auth_service

    def listar(self):
        return self._usuarios.listar()

    def buscar(self, usuario_id):
        usuario = self._usuarios.buscar_por_id(usuario_id)
        if not usuario:
            raise NotFoundError("Usuário não encontrado")
        return usuario

    def criar(self, dados):
        if not dados or not isinstance(dados, dict):
            raise ValidationError("Dados inválidos")
        nome = _campo_texto(dados, "nome")
        email = _campo_texto(dados, "email")
        senha = _campo_texto(dados, "senha")
        if not nome or not email or not senha:
            raise ValidationError("Nome, email e senha são obrigatórios")

        usuario_id = self._usuarios.criar(nome, email, generate_password_hash(senha), TIPO_CLIENTE)
        self._db.commit()
        logger.info("Usuário criado: %s", email)
        return usuario_id

    def login(self, dados):
        dados = dados if isinstance(dados, dict) else {}
        email = _campo_texto(dados, "email")
        senha = _campo_texto(dados, "senha")
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")

        for usuario in self._usuarios.buscar_por_email(email):
            if _senha_confere(senha, usuario.senha or ""):
                if not usuario.senha.startswith(PREFIXOS_HASH):
                    self._usuarios.atualizar_senha(usuario.id, generate_password_hash(senha))
                    self._db.commit()
                logger.info("Login bem-sucedido: %s", email)
                return usuario, self._auth.emitir_token(usuario)

        logger.info("Login falhou: %s", email)
        raise AuthenticationError("Email ou senha inválidos", sucesso=False)
