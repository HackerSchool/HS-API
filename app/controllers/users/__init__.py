from flask import Blueprint

bp = Blueprint('members', __name__)

from app.controllers.users import routes