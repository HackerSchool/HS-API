from flask import Blueprint

bp = Blueprint('member_projects', __name__)

from app.api.member_projects import routes