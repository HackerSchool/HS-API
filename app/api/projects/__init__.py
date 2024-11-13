from flask import Blueprint

bp = Blueprint('projects', __name__)

from app.api.projects import routes