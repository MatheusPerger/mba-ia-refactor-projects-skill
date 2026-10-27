from flask import Flask
from flask_cors import CORS

from config.database import db
from config.settings import Settings
from controllers.category_controller import CategoryController
from controllers.report_controller import ReportController
from controllers.task_controller import TaskController
from controllers.user_controller import UserController
from middlewares.auth import AuthMiddleware
from middlewares.error_handler import register_error_handlers
from middlewares.logging_config import configure_logging
from repositories.category_repository import CategoryRepository
from repositories.task_repository import TaskRepository
from repositories.user_repository import UserRepository
from routes.category_routes import create_category_blueprint
from routes.health_routes import create_health_blueprint
from routes.report_routes import create_report_blueprint
from routes.task_routes import create_task_blueprint
from routes.user_routes import create_user_blueprint
from services.auth_service import AuthService
from services.category_service import CategoryService
from services.report_service import ReportService
from services.task_service import TaskService
from services.user_service import UserService
import models  # noqa: F401  registra as entidades no SQLAlchemy


def create_app(settings):
    configure_logging(settings.LOG_LEVEL)

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    task_repository = TaskRepository()
    user_repository = UserRepository()
    category_repository = CategoryRepository()

    auth_service = AuthService(user_repository, settings.SECRET_KEY, settings.TOKEN_MAX_AGE_SECONDS)
    auth = AuthMiddleware(auth_service)

    task_controller = TaskController(TaskService(task_repository, user_repository, category_repository))
    user_controller = UserController(UserService(user_repository, task_repository), auth_service, auth)
    category_controller = CategoryController(CategoryService(category_repository, task_repository))
    report_controller = ReportController(ReportService(task_repository, user_repository, category_repository))

    app.register_blueprint(create_task_blueprint(task_controller))
    app.register_blueprint(create_user_blueprint(user_controller, auth))
    app.register_blueprint(create_category_blueprint(category_controller))
    app.register_blueprint(create_report_blueprint(report_controller, auth))
    app.register_blueprint(create_health_blueprint())
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


settings = Settings.from_env()
app = create_app(settings)

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
