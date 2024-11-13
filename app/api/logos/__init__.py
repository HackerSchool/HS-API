from flask import Blueprint

bp = Blueprint('logos', __name__)

from app.api.logos import routes