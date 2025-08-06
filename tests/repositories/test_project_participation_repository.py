import pytest

from app import create_app
from app.config import Config
from app.extensions import db
from app.utils import ProjectStateEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.project_participation_model import ProjectParticipation

base_member = {
    "username": "username",
    "name": "name",
    "email": "email",
}

base_project = {
    "name": "proj_name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE
}

base_participation = {
    "join_date": "1970-01-01"
}

@pytest.fixture(scope="function")
def app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    app = create_app()
    with app.app_context():
        db.create_all()
        yield
        db.session.commit() # flush transactions or it won't be able to drop
        db.drop_all()

@pytest.fixture
def member():
    return Member(**base_member)

@pytest.fixture
def project():
    return Project(**base_project)
