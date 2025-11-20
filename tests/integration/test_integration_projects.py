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


def test_dev_create_project(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.post("/projects", json=base_project)
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k in base_project:
        assert k in rsp.json and rsp.json[k] == base_project[k]


def test_member_create_project(logged_in_member: FlaskClient):
    rsp = logged_in_member.post("/projects", json=base_project)
    assert rsp.status_code == HTTPStatus.FORBIDDEN
    assert rsp.mimetype == "application/json"


def test_sysadmin_create_project_conflict_name(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.post("/projects", json={"name": base_project["name"] + "1", "start_date": "1970-01-01",
                                                     "state": ProjectStateEnum.ACTIVE})
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_sysadmin_create_project_conflict_slug(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.post("/projects", json={"name": base_project["name"] + "1 ", "start_date": "1970-01-01",
                                                     "state": ProjectStateEnum.ACTIVE})
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_sysadmin_get_all_projects(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.get("/projects")
    assert rsp.status_code == HTTPStatus.OK
    assert rsp.mimetype == "application/json"
    data = rsp.json
    assert isinstance(data, list)
    assert len(data) == len(roles)  # since we add one project per role in populate_db
    for project in data:
        assert "name" in project
        assert "state" in project
        assert "start_date" in project
        assert "slug" in project


def test_sysadmin_get_project_by_slug(logged_in_sysadmin: FlaskClient):
    # Slug for "name0" should just be "name0" based on slugify()
    rsp = logged_in_sysadmin.get("/projects/name0")
    assert rsp.status_code == HTTPStatus.OK
    assert rsp.mimetype == "application/json"
    project = rsp.json
    assert project["name"] == "name0"
    assert project["slug"] == "name0"
    assert project["state"] == ProjectStateEnum.ACTIVE


def test_sysadmin_get_project_by_slug_not_found(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.get("/projects/nonexistent-slug")
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"
    assert "description" in rsp.json and "not found" in rsp.json["description"].lower()


def test_sysadmin_update_project_name(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put(
        "/projects/name0",
        json={"name": "new_project_name"}
    )
    assert rsp.status_code == HTTPStatus.OK
    assert rsp.mimetype == "application/json"
    data = rsp.json
    assert data["name"] == "new_project_name"
    assert data["slug"] == "new-project-name"


def test_sysadmin_update_nonexistent_project(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put(
        "/projects/nonexistent-slug",
        json={"name": "does_not_matter"}
    )
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"
    assert "description" in rsp.json and "not found" in rsp.json["description"].lower()


def test_sysadmin_update_project_conflict_slug(logged_in_sysadmin: FlaskClient):
    # "name1" already exists in DB, so changing name0 to "name1" should conflict
    rsp = logged_in_sysadmin.put(
        "/projects/name0",
        json={"name": "name1"}
    )
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_member_cannot_update_project(logged_in_member: FlaskClient):
    rsp = logged_in_member.put(
        "/projects/name0",
        json={"name": "new_name"}
    )
    assert rsp.status_code == HTTPStatus.FORBIDDEN
    assert rsp.mimetype == "application/json"


def test_sysadmin_partial_update(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put(
        "/projects/name0",
        json={"state": ProjectStateEnum.INACTIVE}
    )
    assert rsp.status_code == HTTPStatus.OK
    assert rsp.mimetype == "application/json"
    data = rsp.json
    assert data["name"] == "name0"  # name should stay the same
    assert data["state"] == ProjectStateEnum.INACTIVE


def test_sysadmin_delete_project(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.delete("/projects/name0")
    assert rsp.status_code == HTTPStatus.OK
    assert rsp.mimetype == "application/json"
    data = rsp.json
    assert data["description"] == "Project deleted successfully"
    assert data["name"] == "name0"

    # Confirm it's really gone
    rsp_check = logged_in_sysadmin.get("/projects/name0")
    assert rsp_check.status_code == HTTPStatus.NOT_FOUND


def test_sysadmin_delete_nonexistent_project(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.delete("/projects/nonexistent-slug")
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"
    assert "description" in rsp.json and "not found" in rsp.json["description"].lower()


def test_member_cannot_delete_project(logged_in_member: FlaskClient):
    rsp = logged_in_member.delete("/projects/name0")
    assert rsp.status_code == HTTPStatus.FORBIDDEN
    assert rsp.mimetype == "application/json"
