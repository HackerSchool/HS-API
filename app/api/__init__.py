from flask import Flask
from flask_session import Session

from app.config import Config
from app.api.extensions import session
from app.api.extensions import db_handler
from app.api.extensions import tags_handler
from app.api.extensions import logos_handler

def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Initialize extensions
    session.init_app(flask_app)
    db_handler.init_app(flask_app)
    tags_handler.init_app(flask_app)
    logos_handler.init_app(flask_app)

    # Register blueprints
    from app.api.auth import bp as auth_bp
    flask_app.register_blueprint(auth_bp)

    from app.api.members import bp as members_bp
    flask_app.register_blueprint(members_bp, url_prefix="/members")

    from app.api.projects import bp as projects_bp
    flask_app.register_blueprint(projects_bp, url_prefix="/projects")

    from app.api.member_projects import bp as member_projects_bp
    flask_app.register_blueprint(member_projects_bp, url_prefix="/link")

    from app.api.logos import bp as logos_bp
    flask_app.register_blueprint(logos_bp)

    return flask_app

entry = create_app()