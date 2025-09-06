import logging
import os

import sentry_sdk
from flask import Flask
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.auth.auth_controller import AuthController
from app.auth.fenix.fenix_service import FenixService
from app.auth.scopes.system_scopes import SystemScopes

from app.commands import register_cli_commands
from app.config import Config

from app.errors import handle_validation_error, handle_http_exception

from app.extensions import db
from app.extensions import migrate
from app.extensions import session

from app.repositories.member_repository import MemberRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository

from app.controllers.member_controller import create_member_bp
from app.controllers.project_controller import create_project_bp
from app.controllers.project_participation_controller import create_participation_bp
from app.controllers.login_controller import create_login_bp
from app.controllers.image_controller import create_images_bp
from app.controllers.task_controller import create_task_bp


def create_app(config_class=Config, *, member_repo=None, project_repo=None, participation_repo=None, task_repo=None,
               fenix_service=None, auth_controller=None):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)
    CORS(flask_app, supports_credentials=True, resources={r"/*": {"origins": config_class.ORIGINS_WHITELIST}})

    session.init_app(flask_app)
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    if flask_app.config["SENTRY_DSN"]:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # capture info and above as breadcrumbs
            event_level=logging.ERROR  # send errors and above as events to Sentry
        )
        sentry_sdk.init(
            dsn=flask_app.config["SENTRY_DSN"],
            integrations=[
                FlaskIntegration(),
                sentry_logging,
            ],
        )

    if member_repo is None:
        member_repo = MemberRepository(db=db)
    if project_repo is None:
        project_repo = ProjectRepository(db=db)
    if participation_repo is None:
        participation_repo = ProjectParticipationRepository(db=db)

    if task_repo is None:
        task_repo = TaskRepository(db=db)

    if fenix_service is None:
        fenix_service = FenixService(
            client_id=flask_app.config["CLIENT_ID"],
            client_secret=flask_app.config["CLIENT_SECRET"],
            root_uri=flask_app.config["ROOT_URI"],
            redirect_endpoint=flask_app.config["FENIX_REDIRECT_ENDPOINT"],
        )

    if auth_controller is None:
        auth_controller = AuthController(
            enabled=flask_app.config["ENABLED_ACCESS_CONTROL"],
            system_scopes=SystemScopes.from_yaml_config(flask_app.config["ROLES_PATH"]),
            member_repo=member_repo,
            project_repo=project_repo,
            participation_repo=participation_repo,
        )

    member_bp = create_member_bp(member_repo=member_repo, auth_controller=auth_controller)
    flask_app.register_blueprint(member_bp)

    project_bp = create_project_bp(project_repo=project_repo, auth_controller=auth_controller)
    flask_app.register_blueprint(project_bp)

    participation_bp = create_participation_bp(participation_repo=participation_repo, project_repo=project_repo,
                                               member_repo=member_repo,
                                               auth_controller=auth_controller)
    flask_app.register_blueprint(participation_bp)

    task_bp = create_task_bp(task_repo=task_repo, participation_repo=participation_repo,
                        project_repo=project_repo, member_repo=member_repo, auth_controller=auth_controller)
    flask_app.register_blueprint(task_bp)

    images_bp = create_images_bp(flask_app.config["IMAGES_PATH"], member_repo=member_repo, project_repo=project_repo,
                                 auth_controller=auth_controller)
    flask_app.register_blueprint(images_bp)

    login_bp = create_login_bp(member_repo=member_repo, auth_controller=auth_controller, fenix_service=fenix_service)
    flask_app.register_blueprint(login_bp)

    from werkzeug.exceptions import HTTPException
    flask_app.register_error_handler(HTTPException, handle_http_exception)
    from pydantic import ValidationError
    flask_app.register_error_handler(ValidationError, handle_validation_error)

    register_cli_commands(flask_app)

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
