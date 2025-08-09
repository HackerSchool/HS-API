from http import HTTPStatus

import pytest

from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.config import Config
from app.extensions import db

from app.utils import ProjectStateEnum

from app.models.project_model import Project
from app.models.member_model import Member

base_project = {
    "name": "name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE
}

roles = ["sysadmin", "dev", "finance", "member"]


def populate_db():
    for i, role in enumerate(roles):
        new_project = {
            **base_project,
            "name": base_project["name"] + str(i),
        }
        new_member = {
            "username": role,
            "password": "password",
            "name": role,
            "email": role,
            "ist_id": "ist10000" + str(i),
            "roles": [role]
        }
        project = Project(**new_project)
        member = Member(**new_member)
        db.session.add(member)
        db.session.add(project)
    db.session.commit()


@pytest.fixture()
def app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    Config.SESSION_TYPE = "cachelib"
    Config.ENABLED_ACCESS_CONTROL = "True"
    app = create_app()

    with app.app_context():
        db.create_all()
        populate_db()
        yield app
        db.drop_all()


@pytest.fixture(scope="function")
def logged_in_sysadmin(app: Flask):
    with app.test_client() as client:
        client.post("/login", json={"username": "sysadmin", "password": "password"})
        yield client


@pytest.fixture(scope="function")
def logged_in_member(app: Flask):
    with app.test_client() as client:
        client.post("/login", json={"username": "member", "password": "password"})
        yield client
