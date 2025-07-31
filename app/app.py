import os
import logging

from flask import Flask

from app.config import Config
from app.errors import handle_validation_error, handle_http_exception

from app.access import AccessController
from app.access.permissions.permission_handler import PermissionHandler

from app.extensions import session
from app.extensions import db
from app.extensions import migrate

from app.controllers.member_controller import create_member_bp
from app.controllers.project_controller import create_project_bp
from app.controllers.auth_controller import create_auth_bp

from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository


def create_app(config_class=Config, *, member_repo=None, project_repo=None, access_controller=None):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    session.init_app(flask_app)
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    if member_repo is None:
        member_repo = MemberRepository(db=db)
    if project_repo is None:
        project_repo = ProjectRepository(db=db)

    if access_controller is None:
        access_controller = AccessController(
            enabled=flask_app.config["ENABLED_ACCESS_CONTROL"],
            permission_handler=PermissionHandler.from_yaml_config(flask_app.config["ROLES_PATH"]),
            member_repo=member_repo,
        )

    member_bp = create_member_bp(member_repo=member_repo, access_controller=access_controller)
    flask_app.register_blueprint(member_bp)

    project_bp = create_project_bp(project_repo=project_repo, access_controller=access_controller)
    flask_app.register_blueprint(project_bp)

    auth_bp = create_auth_bp(member_repo=member_repo, access_controller=access_controller)
    flask_app.register_blueprint(auth_bp)

    from werkzeug.exceptions import HTTPException
    flask_app.register_error_handler(HTTPException, handle_http_exception)
    from pydantic import ValidationError
    flask_app.register_error_handler(ValidationError, handle_validation_error)

    return flask_app


def setup_logger(app: Flask):
    """
    If ran with gunicorn simply sets Flask logger to gunicorn ones, configured through cli arguments.
    If ran with Flask development server simply logs at debug level or default to stdout.
    """
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
