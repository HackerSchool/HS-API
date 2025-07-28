import pytest

from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db

from app.repositories.project_repository import ProjectRepository
from app.schemas.update_project_schema import UpdateProjectSchema
from app.models.project_model import Project
from app.utils import ProjectStateEnum, slugify

base_project = {
    "name": "project name",
    "state": ProjectStateEnum.ACTIVE,
    "start_date": "1970-01-01",
}

@pytest.fixture(scope="function")
def app():
    Config.DATABASE_PATH = "sqlite:///:memory:"
    app = create_app()
    with app.app_context():
        db.create_all()
        yield
        db.session.commit()
        db.drop_all()

@pytest.fixture
def project_repository(app):
    return ProjectRepository(db=db)

def test_create_project(project_repository):
    new_project = Project(**base_project)
    project_repository.create_project(new_project)

    project = db.session.execute(select(Project).where(Project._name == new_project.name)).scalars().one_or_none()
    assert project is not None
    assert project.name == new_project.name
    assert project.state == new_project.state
    assert project.start_date == new_project.start_date


def test_get_project_by_name(project_repository):
    project = Project(**base_project)
    db.session.add(project)

    gotten_project = project_repository.get_project_by_name(base_project["name"])
    assert gotten_project is not None
    assert project.name == gotten_project.name
    assert project.start_date == gotten_project.start_date
    assert project.slug == gotten_project.slug
    assert project.state == gotten_project.state

def test_get_project_by_slug(project_repository):
    project = Project(**base_project)
    db.session.add(project)

    gotten_project = project_repository.get_project_by_slug(project.slug)
    assert gotten_project is not None
    assert project.name == gotten_project.name
    assert project.start_date == gotten_project.start_date
    assert project.slug == gotten_project.slug
    assert project.state == gotten_project.state

def test_get_no_project_by_name(app, project_repository: ProjectRepository):
    assert project_repository.get_project_by_name(base_project["name"]) is None

def test_get_no_project_by_slug(app, project_repository: ProjectRepository):
    assert project_repository.get_project_by_slug(slugify(base_project["name"])) is None

def test_get_projects(app, project_repository: ProjectRepository):
    projects: set = set()
    for i in range(3):
        data = {**base_project, "name": base_project["name"] + str(i)}
        project = Project(**data)
        db.session.add(project)
        projects.add(project)

    gotten_projects = project_repository.get_projects()
    assert {p.name for p in projects} == {gp.name for gp in gotten_projects}

def test_update_project(app, project_repository: ProjectRepository):
    project = Project(**base_project)
    db.session.add(project)
    new_data = {
        "name": "new name",
        "state": ProjectStateEnum.INACTIVE,
    }

    update_values = UpdateProjectSchema(**new_data)
    updated_project = project_repository.update_project(project, update_values)

    gotten_project = db.session.execute(select(Project).where(Project._name == project.name)).scalars().one_or_none()
    assert gotten_project.name == updated_project.name
    assert gotten_project.slug == updated_project.slug
    assert gotten_project.start_date == updated_project.start_date

def test_delete_project(app, project_repository: ProjectRepository):
    project = Project(**base_project)
    db.session.add(project)

    name = project_repository.delete_project(project)
    assert name == project.name
    assert db.session.execute(select(Project).where(Project._name == project.name)).scalars().one_or_none() is None

