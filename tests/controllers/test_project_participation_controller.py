from http import HTTPStatus

import pytest

from unittest.mock import MagicMock

from flask.testing import FlaskClient

from app import create_app
from app.utils import ProjectStateEnum

from app.models.project_model import Project
from app.models.member_model import Member
from app.models.project_participation_model import ProjectParticipation

from app.repositories.member_repository import MemberRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.project_repository import ProjectRepository


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

@pytest.fixture
def mock_member_repo():
    return MagicMock()

@pytest.fixture
def mock_project_repo():
    return MagicMock()

@pytest.fixture
def mock_participation_repo():
    return MagicMock()

@pytest.fixture
def client(mock_member_repo, mock_project_repo, mock_participation_repo):
    from app.config import Config
    Config.ENABLED_ACCESS_CONTROL = False

    app = create_app(member_repo=mock_member_repo, project_repo=mock_project_repo, participation_repo=mock_participation_repo)
    with app.test_client() as client:
        yield client

def test_create_participation(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = project
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = None

    part = ProjectParticipation(member=member, project=project , **base_participation)
    mock_participation_repo.create_participation.return_value = part

    rsp = client.post(f'/projects/{project.name}/participations', json={**base_participation, "username": member.username})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == member.username
    assert "project_name" in rsp.json and rsp.json["project_name"] == project.name
    assert "join_date" in rsp.json and rsp.json["join_date"] == part.join_date
    assert "roles" in rsp.json and rsp.json["roles"] == []

def test_create_participation_project_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    mock_project_repo.get_project_by_slug.return_value = None
    rsp = client.post(f'/projects/{base_project["name"]}/participations', json={**base_participation, "username": member.username})
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_create_participation_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    project = Project(**base_project)
    mock_project_repo.get_project_by_slug.return_value = project
    mock_member_repo.get_member_by_username.return_value = None
    rsp = client.post(f'/projects/{project.name}/participations',
                      json={**base_participation, "username": base_member["username"]})
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"


def test_create_participation_conflict(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = project
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = not None

    part = ProjectParticipation(member=member, project=project , **base_participation)
    mock_participation_repo.create_participation.return_value = part

    rsp = client.post(f'/projects/{project.name}/participations', json={**base_participation, "username": member.username})
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_get_participation(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)
    part = ProjectParticipation(member=member, project=project , **base_participation)

    mock_project_repo.get_project_by_slug.return_value = project

    rsp = client.get(f'/projects/{project.name}/participations')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert isinstance(rsp.json, list)
    assert len(rsp.json) == 1
    assert "join_date" in rsp.json[0] and rsp.json[0]["join_date"] == part.join_date
    assert "username" in rsp.json[0] and rsp.json[0]["username"] == member.username

def test_get_participation_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    mock_project_repo.get_project_by_slug.return_value = None

    rsp = client.get(f'/projects/{base_project["name"]}/participations')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_get_member_participation(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)
    part = ProjectParticipation(member=member, project=project , **base_participation)

    mock_project_repo.get_project_by_slug.return_value = not None
    mock_member_repo.get_member_by_username.return_value = member

    rsp = client.get(f'/members/{member.username}/participations')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert isinstance(rsp.json, list)
    assert len(rsp.json) == 1
    assert "join_date" in rsp.json[0] and rsp.json[0]["join_date"] == part.join_date
    assert "project_name" in rsp.json[0] and rsp.json[0]["project_name"] == project.name

def test_get_member_participation_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    mock_project_repo.get_project_by_slug.return_value = not None
    mock_member_repo.get_member_by_username.return_value = None

    rsp = client.get(f'/members/{base_member["username"]}/participations')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_get_participation_by_username(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)
    part = ProjectParticipation(member=member, project=project , **base_participation)

    mock_project_repo.get_project_by_slug.return_value = member
    mock_member_repo.get_member_by_username.return_value = project
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = part

    rsp = client.get(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == member.username
    assert "join_date" in rsp.json and rsp.json["join_date"] == part.join_date
    assert "roles" in rsp.json and rsp.json["roles"] == []

def test_get_participation_by_username_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)
    part = ProjectParticipation(member=member, project=project, **base_participation)

    mock_project_repo.get_project_by_slug.return_value = member
    mock_member_repo.get_member_by_username.return_value = project
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = None

    rsp = client.get(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_get_participation_by_username_project_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_project_repo.get_project_by_slug.return_value = member
    mock_member_repo.get_member_by_username.return_value = None

    rsp = client.get(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_get_participation_by_username_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_project_repo.get_project_by_slug.return_value = None
    mock_member_repo.get_member_by_username.return_value = project

    rsp = client.get(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_update_participation_by_username(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = project

    part = ProjectParticipation(member=member, project=project , **base_participation)
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = part
    mock_participation_repo.update_participation.return_value = ProjectParticipation(member=member, project=project, join_date="1971-01-01")

    rsp = client.put(f'/projects/{project.name}/participations/{member.username}', json={"join_date": "1971-01-01"})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == member.username
    assert "project_name" in rsp.json and rsp.json["project_name"] == project.name
    assert "join_date" in rsp.json and rsp.json["join_date"] == "1971-01-01"
    assert "roles" in rsp.json and rsp.json["roles"] == []

def test_update_participation_by_username_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = project

    part = ProjectParticipation(member=member, project=project , **base_participation)
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = None

    rsp = client.put(f'/projects/{project.name}/participations/{member.username}', json={"join_date": "1971-01-01"})
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_update_participation_by_username_project_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = None

    rsp = client.put(f'/projects/{project.name}/participations/{member.username}', json={"join_date": "1971-01-01"})
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_update_participation_by_username_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = None
    mock_project_repo.get_project_by_slug.return_value = project

    rsp = client.put(f'/projects/{project.name}/participations/{member.username}', json={"join_date": "1971-01-01"})
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"


def test_delete_participation(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = project

    part = ProjectParticipation(member=member, project=project , **base_participation)
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = part
    mock_participation_repo.delete_participation.return_value = (member.username, project.name)

    rsp = client.delete(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == member.username
    assert "project_name" in rsp.json and rsp.json["project_name"] == project.name


def test_delete_participation_by_username_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = project
    mock_participation_repo.get_participation_by_project_and_member_id.return_value = None

    rsp = client.delete(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_delete_participation_by_username_project_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = member
    mock_project_repo.get_project_by_slug.return_value = None

    rsp = client.delete(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_delete_participation_by_username_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository, mock_project_repo: ProjectRepository, mock_participation_repo: ProjectParticipationRepository):
    member = Member(**base_member)
    project = Project(**base_project)

    mock_member_repo.get_member_by_username.return_value = None
    mock_project_repo.get_project_by_slug.return_value = project

    rsp = client.delete(f'/projects/{project.name}/participations/{member.username}')
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"


