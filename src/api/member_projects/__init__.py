from flask import Blueprint

bp = Blueprint('member_projects', __name__)

from api.member_projects import routes