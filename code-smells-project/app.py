from flask import Flask
from flask_cors import CORS

from config import settings
from config.database import Database
from config.logger import configurar_logging
from controllers.pedido_controller import PedidoController
from controllers.produto_controller import ProdutoController
from controllers.relatorio_controller import RelatorioController
from controllers.sistema_controller import SistemaController
from controllers.usuario_controller import UsuarioController
from middlewares.auth import AuthMiddleware
from middlewares.error_handler import registrar_error_handlers
from repositories.pedido_repository import PedidoRepository
from repositories.produto_repository import ProdutoRepository
from repositories.sistema_repository import SistemaRepository
from repositories.usuario_repository import UsuarioRepository
from routes import pedido_routes, produto_routes, relatorio_routes, sistema_routes, usuario_routes
from services.auth_service import AuthService
from services.pedido_service import PedidoService
from services.produto_service import ProdutoService
from services.relatorio_service import RelatorioService
from services.sistema_service import SistemaService
from services.usuario_service import UsuarioService


def create_app():
    settings.validar()
    configurar_logging(settings.LOG_LEVEL)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    CORS(app)

    db = Database()
    db.init()
    app.teardown_appcontext(db.close)

    produtos = ProdutoRepository(db)
    usuarios = UsuarioRepository(db)
    pedidos = PedidoRepository(db)
    sistema = SistemaRepository(db)

    auth_service = AuthService(settings.SECRET_KEY, settings.TOKEN_MAX_AGE_SECONDS)
    auth = AuthMiddleware(auth_service)

    app.register_blueprint(produto_routes.criar_blueprint(
        ProdutoController(ProdutoService(db, produtos)), auth))
    app.register_blueprint(usuario_routes.criar_blueprint(
        UsuarioController(UsuarioService(db, usuarios, auth_service)), auth))
    app.register_blueprint(pedido_routes.criar_blueprint(
        PedidoController(PedidoService(db, pedidos, produtos)), auth))
    app.register_blueprint(relatorio_routes.criar_blueprint(
        RelatorioController(RelatorioService(pedidos)), auth))
    app.register_blueprint(sistema_routes.criar_blueprint(
        SistemaController(SistemaService(db, sistema, produtos, usuarios, pedidos)), auth))

    registrar_error_handlers(app)
    return app


if __name__ == "__main__":
    create_app().run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
