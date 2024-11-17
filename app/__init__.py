import os
import logging

from flask import Flask
from flask_cors import CORS

from app.config import Config, basedir
from app.extensions import session
from app.extensions import db
from app.extensions import migrate
from app.extensions import roles_handler
from app.extensions import logos_handler


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

    roles_handler.init_app(flask_app)
    logos_handler.init_app(flask_app)

    register_blueprints(flask_app)
    register_error_handlers(flask_app)
    register_commands(flask_app)

    if (frontend_uri := flask_app.config.get("FRONTEND_URI", "")) != "":
        CORS(flask_app, origins=[frontend_uri], supports_credentials=True)

    setup_logger(flask_app)

    return flask_app

def register_blueprints(app: Flask):
    from app.api.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.api.members import bp as members_bp
    app.register_blueprint(members_bp, url_prefix="/members")

    from app.api.projects import bp as projects_bp
    app.register_blueprint(projects_bp, url_prefix="/projects")

    from app.api.logos import bp as logos_bp
    app.register_blueprint(logos_bp)

def register_error_handlers(app: Flask):
    from app.api.errors import handle_http_exception
    from werkzeug.exceptions import HTTPException
    app.register_error_handler(HTTPException, handle_http_exception)

    # Register error handlers
    from app.api.errors import handle_api_error, APIError
    app.register_error_handler(APIError, handle_api_error)

    # TODO: Should custom exceptions be prefered to ValueError? 
    from app.api.errors import handle_invalid_input
    app.register_error_handler(ValueError, handle_invalid_input)

    from sqlalchemy import exc
    from app.api.errors import handle_db_integrity_exception, handle_db_exceptions
    app.register_error_handler(exc.IntegrityError, handle_db_integrity_exception)
    app.register_error_handler(exc.SQLAlchemyError, handle_db_exceptions)

def register_commands(app: Flask):
    from app.extensions import register_create_admin_user_command, register_initialize_db_command, register_populate_dummy_db_command 
    register_initialize_db_command(app)
    register_create_admin_user_command(app)
    register_populate_dummy_db_command(app)

def setup_logger(app: Flask):
    """ 
    If ran with gunicorn simply sets Flask logger to gunicorn ones, configured through cli arguments. 
    If ran with Flask development server simply logs at debug level or default to stdout. """
    if app.debug:
        app.logger.setLevel(logging.DEBUG)
        return 

    # create logs folder
    logs_path = app.config.get("LOGS_PATH")
    log_dir = os.path.dirname(logs_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # ran in gunicorn, use gunicorn handlers set through cli arguments
    if __name__ != '__main__':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
        return
