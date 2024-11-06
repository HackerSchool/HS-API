from flask import Flask

from app.config import Config
from app.extensions import session
from app.extensions import db
from app.extensions import tags_handler
from app.extensions import logos_handler

def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Initialize extensions
    session.init_app(flask_app)
    db.init_app(flask_app)
    tags_handler.init_app(flask_app)
    logos_handler.init_app(flask_app)

    # Register blueprints
    from app.api.auth import bp as auth_bp
    flask_app.register_blueprint(auth_bp)

    from app.api.members import bp as members_bp
    flask_app.register_blueprint(members_bp, url_prefix="/members")

    from app.api.projects import bp as projects_bp
    flask_app.register_blueprint(projects_bp, url_prefix="/projects")

    from app.api.logos import bp as logos_bp
    flask_app.register_blueprint(logos_bp)

    from app.api.errors import handle_exception
    from werkzeug.exceptions import HTTPException
    flask_app.register_error_handler(HTTPException, handle_exception)

    # Register error handlers
    from app.api.errors import handle_api_error, APIError
    flask_app.register_error_handler(APIError, handle_api_error)

    # TODO: Should custom exceptions be prefered to ValueError? 
    from app.api.errors import handle_invalid_input
    flask_app.register_error_handler(ValueError, handle_invalid_input)

    from sqlalchemy import exc
    from app.api.errors import handle_db_integrity_exception, handle_db_exceptions
    flask_app.register_error_handler(exc.IntegrityError, handle_db_integrity_exception)
    flask_app.register_error_handler(exc.SQLAlchemyError, handle_db_exceptions)

    return flask_app

entry = create_app()