from flask import Flask

from config import Config
from api.extensions import db_handler
from api.extensions import tags_handler
from api.extensions import logos_handler

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db_handler.init_app(app)
    tags_handler.init_app(app)
    logos_handler.init_app(app)

    # Register blueprints
    from api.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from api.members import bp as members_bp
    app.register_blueprint(members_bp)

    from api.projects import bp as projects_bp
    app.register_blueprint(projects_bp)

    from api.member_projects import bp as member_projects_bp
    app.register_blueprint(member_projects_bp)

    from api.logos import bp as logos_bp
    app.register_blueprint(logos_bp)

    return app