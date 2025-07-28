from http import HTTPStatus

import pytest

from unittest.mock import MagicMock

from flask.testing import FlaskClient

from app.utils import slugify, ProjectStateEnum

from app import create_app
from app.extensions import db

from app.schemas.project_schema import ProjectSchema
from app.models.project_model import Project
from app.repositories.project_repository import ProjectRepository
from app.utils import ProjectStateEnum

base_project = {
    "name": "project name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE,
}

@pytest.fixture
def mock_project_repo():
    return MagicMock()

@pytest.fixture
def app(mock_project_repo):
    app = create_app(project_repo=mock_project_repo)
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app, mock_project_repo):
    with app.test_client() as client:
        yield client

def test_get_project(client: FlaskClient, mock_project_repo: ProjectRepository):
    mock_project_repo.get_project_by_slug.return_value = Project.from_schema(ProjectSchema(**base_project))
    rsp = client.get(f'/projects/{slugify(base_project["name"])}')

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in base_project.items():
        assert rsp.json[k] == v

def test_get_project_not_found(client: FlaskClient, mock_project_repo: ProjectRepository):
    mock_project_repo.get_project_by_slug.return_value = None
    rsp = client.get(f'/projects/{slugify(base_project["name"])}')

    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_create_project(client: FlaskClient, mock_project_repo: ProjectRepository):
    project = Project(**base_project)
    schema = ProjectSchema.from_project(project)
    mock_project_repo.get_project_by_name.return_value = None
    mock_project_repo.get_project_by_slug.return_value = None
    mock_project_repo.create_project.return_value = project

    rsp = client.post(f'/projects', json=schema.model_dump())
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"

def test_create_project_duplicate_name(client: FlaskClient, mock_project_repo: ProjectRepository):
    project = Project(**base_project)
    schema = ProjectSchema.from_project(project)
    mock_project_repo.get_project_by_name.return_value = not None

    rsp = client.post(f'/projects', json=schema.model_dump())
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"

def test_create_project_duplicate_slug(client: FlaskClient, mock_project_repo: ProjectRepository):
    project = Project(**base_project)
    schema = ProjectSchema.from_project(project)
    mock_project_repo.get_project_by_name.return_value = None
    mock_project_repo.get_project_by_slug.return_value = not None

    rsp = client.post(f'/projects', json=schema.model_dump())
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"

def test_get_projects_empty(client: FlaskClient, mock_project_repo):
    mock_project_repo.get_projects.return_value = []
    rsp = client.get("/projects")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json == []

def test_get_projects(client: FlaskClient, mock_project_repo: ProjectRepository):
    # Quick explanation: Use sets to determine that the response matches the mock,
    #   because sets don't care for order, unlike lists or tuples.
    # Needs frozenset because dicts aren't hashable and can't be put into sets.
    projects: list = []
    expected_projects: set = set()
    for i in range(3):
        name = base_project["name"] + str(i)
        p = Project(**base_project)
        p.name = name
        projects.append(p)

        expected = {**base_project, "name": name}
        expected_projects.add(frozenset(expected.items()))

    mock_project_repo.get_projects.return_value = projects
    rsp = client.get("/projects")

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert isinstance(rsp.json, list)
    assert len(rsp.json) == 3
    # remove all keys not found in base_user from each json object
    ret_projects: set = set()
    for i in range(3):
        filtered_obj = {k: v for k, v in rsp.json[i].items() if k in base_project.keys()}
        ret_projects.add(frozenset(filtered_obj.items()))

    assert ret_projects == expected_projects

def test_update_project_not_found(client: FlaskClient, mock_project_repo: ProjectRepository):
    mock_project_repo.get_project_by_slug.return_value = None
    rsp = client.put(f"/projects/{slugify(base_project['name'])}", json=base_project)
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_update_project_conflict(client: FlaskClient, mock_project_repo: ProjectRepository):
    mock_project_repo.get_project_by_slug.return_value = not None
    rsp = client.put(f"/projects/{slugify(base_project['name'])}", json=base_project)
    assert rsp.status_code == HTTPStatus.CONFLICT.value
    assert rsp.mimetype == "application/json"

def test_update_project(client: FlaskClient, mock_project_repo: ProjectRepository):
    update_project = {**base_project, "start_date": "1980-01-01"}
    mock_project_repo.get_project_by_slug.return_value = not None
    mock_project_repo.update_project.return_value = Project(**update_project)

    rsp = client.put(f"/projects/{slugify(base_project['name'])}", json={"start_date": "1980-01-01"})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in update_project.items():
        assert rsp.json[k] == v

def test_delete_project_not_found(client: FlaskClient, mock_project_repo: ProjectRepository):
    mock_project_repo.get_project_by_slug.return_value = None
    rsp = client.delete(f"/projects/{slugify(base_project['name'])}")
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_delete_project(client: FlaskClient, mock_project_repo: ProjectRepository):
    mock_project_repo.get_project_by_slug.return_value = not None
    mock_project_repo.delete_project.return_value = base_project["name"]
    rsp = client.delete(f"/projects/{slugify(base_project['name'])}")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["name"] == base_project["name"]

