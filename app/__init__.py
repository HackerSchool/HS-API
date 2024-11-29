import logging
import os

from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, session
from app.services.fenix import fenix_service
from app.services.logos import logos_service
from app.services.roles import roles_service


def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Initialize extensions
    session.init_app(flask_app)

    db_dir = os.path.dirname(flask_app.config.get("DATABASE_PATH"))
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    roles_service.init_app(flask_app)
    logos_service.init_app(flask_app)
    fenix_service.init_app(flask_app)

    register_blueprints(flask_app)
    register_error_handlers(flask_app)
    register_commands(flask_app)

    if (frontend_uri := flask_app.config.get("FRONTEND_URI", "")) != "":
        CORS(flask_app, origins=[frontend_uri], supports_credentials=True)

    setup_logger(flask_app)

    return flask_app


def register_blueprints(app: Flask):
    from app.controllers.auth import bp as auth_bp

    app.register_blueprint(auth_bp)

    from app.controllers.users import bp as members_bp

    app.register_blueprint(members_bp, url_prefix="/users")

    # from app.controllers.projects import bp as projects_bp

    # app.register_blueprint(projects_bp, url_prefix="/projects")


def register_error_handlers(app: Flask):
    from werkzeug.exceptions import HTTPException

    from app.errors import handle_http_exception

    app.register_error_handler(HTTPException, handle_http_exception)

    # TODO: Should custom exceptions be prefered to ValueError?
    from app.errors import handle_value_error

    app.register_error_handler(ValueError, handle_value_error)

    from sqlalchemy import exc

    from app.errors import handle_db_exceptions, handle_db_integrity_exception

    app.register_error_handler(exc.IntegrityError, handle_db_integrity_exception)
    app.register_error_handler(exc.SQLAlchemyError, handle_db_exceptions)


def register_commands(app: Flask):
    from app.commands.commands import (
        register_create_admin_user_command,
        register_initialize_db_command,
        register_populate_dummy_db_command,
        register_test_command,
    )

    register_initialize_db_command(app)
    register_create_admin_user_command(app)
    register_populate_dummy_db_command(app)
    register_test_command(app)


def setup_logger(app: Flask):
    """
    If ran with gunicorn simply sets Flask logger to gunicorn ones, configured through cli arguments.
    If ran with Flask development server simply logs at debug level or default to stdout."""
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        return

    # create logs folder
    logs_path = app.config.get("LOGS_PATH")
    log_dir = os.path.dirname(logs_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # ran in gunicorn, use gunicorn handlers set through cli arguments
    if __name__ != "__main__":
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
        return
