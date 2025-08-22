from http import HTTPStatus
from unittest.mock import MagicMock
import pytest

from flask.testing import FlaskClient

from app import create_app
from app.utils import ProjectStateEnum, PointTypeEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.season_model import Season
from app.models.project_participation_model import ProjectParticipation
from app.models.task_model import Task

from app.schemas.task_schema import TaskSchema
from app.schemas.update_task_schema import UpdateTaskSchema

from app.repositories.task_repository import TaskRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.season_repository import SeasonRepository


base_member = {
    "username": "username",
    "name": "name",
    "email": "email",
}

base_project = {
    "name": "proj_name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE,
}

base_participation = {
    "join_date": "1970-01-01",
}

base_season = {
    "season_number": 1,
    "start_date": "1970-01-01",
    "end_date": "1970-12-31",
}

base_task = {
    "point_type": PointTypeEnum.PJ,
    "points": 1,
    "description": "description",
    "finished_at": None,
}

payload_create = {
    "username": base_member["username"],
    "project_name": base_project["name"],
    "season_number": base_season["season_number"],
    "point_type": base_task["point_type"],
    "points": base_task["points"],
    "description": base_task["description"],
    "finished_at": base_task["finished_at"],
}


@pytest.fixture
def mock_repos():
    return {
        "task_repo": MagicMock(),
        "member_repo": MagicMock(),
        "project_repo": MagicMock(),
        "participation_repo": MagicMock(),
        "season_repo": MagicMock(),
    }


@pytest.fixture
def client(mock_repos):
    from app.config import Config
    Config.ENABLED_ACCESS_CONTROL = False

    app = create_app(
        task_repo=mock_repos["task_repo"],
        member_repo=mock_repos["member_repo"],
        project_repo=mock_repos["project_repo"],
        participation_repo=mock_repos["participation_repo"],
        season_repo=mock_repos["season_repo"],
    )
    with app.test_client() as client:
        yield client


def _wire_targets(mock_repos):
    member = Member(**base_member)
    project = Project(**base_project)
    season = Season(**base_season)
    participation = ProjectParticipation(member=member, project=project, **base_participation)

    mock_repos["member_repo"].get_member_by_username.return_value = member
    mock_repos["project_repo"].get_project_by_name.return_value = project
    mock_repos["participation_repo"].get_pp_by_project_and_member_id.return_value = participation
    mock_repos["season_repo"].get_season_by_number.return_value = season

    return member, project, participation, season


def test_create_task_ok(client: FlaskClient, mock_repos):
    _, _, participation, season = _wire_targets(mock_repos)

    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = None

    created = Task(participation=participation, season=season, **base_task)
    mock_repos["task_repo"].create_task.return_value = created

    rsp = client.post("/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["username"] == payload_create["username"]
    assert rsp.json["project_name"] == payload_create["project_name"]
    assert rsp.json["season_number"] == payload_create["season_number"]
    assert rsp.json["point_type"] == payload_create["point_type"]
    assert rsp.json["points"] == payload_create["points"]
    assert rsp.json["description"] == payload_create["description"]
    assert rsp.json["finished_at"] == payload_create["finished_at"]


def test_create_task_conflict(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = object()

    rsp = client.post("/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_create_task_member_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = None
    rsp = client.post("/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_create_task_project_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_name.return_value = None

    rsp = client.post("/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_create_task_participation_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_name.return_value = Project(**base_project)
    mock_repos["participation_repo"].get_pp_by_project_and_member_id.return_value = None

    rsp = client.post("/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_create_task_season_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_name.return_value = Project(**base_project)
    mock_repos["participation_repo"].get_pp_by_project_and_member_id.return_value = ProjectParticipation(
        member=Member(**base_member), project=Project(**base_project), **base_participation
    )
    mock_repos["season_repo"].get_season_by_number.return_value = None

    rsp = client.post("/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_ok(client: FlaskClient, mock_repos):
    _, _, participation, season = _wire_targets(mock_repos)

    t = Task(participation=participation, season=season, **base_task)
    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = t

    rsp = client.get(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["username"] == base_member["username"]
    assert rsp.json["project_name"] == base_project["name"]
    assert rsp.json["season_number"] == base_season["season_number"]


def test_get_task_not_found(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = None

    rsp = client.get(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_get_task_member_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = None
    rsp = client.get(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_project_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_name.return_value = None
    rsp = client.get(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_participation_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_name.return_value = Project(**base_project)
    mock_repos["participation_repo"].get_pp_by_project_and_member_id.return_value = None
    rsp = client.get(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_season_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_name.return_value = Project(**base_project)
    mock_repos["participation_repo"].get_pp_by_project_and_member_id.return_value = ProjectParticipation(
        member=Member(**base_member), project=Project(**base_project), **base_participation
    )
    mock_repos["season_repo"].get_season_by_number.return_value = None
    rsp = client.get(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_update_task_not_found(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = None

    payload = UpdateTaskSchema(
        point_type=PointTypeEnum.PJ, points=2, description="upd", finished_at="1970-01-02"
    ).model_dump()
    rsp = client.put(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}', json=payload)
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_update_task_ok(client: FlaskClient, mock_repos):
    _, _, participation, season = _wire_targets(mock_repos)

    current = Task(participation=participation, season=season, **base_task)
    updated = Task(
        participation=participation, season=season,
        point_type=PointTypeEnum.PJ, points=5, description="updated", finished_at="1970-01-02"
    )

    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = current
    mock_repos["task_repo"].update_task.return_value = updated

    payload = UpdateTaskSchema(
        point_type=PointTypeEnum.PJ, points=5, description="updated", finished_at="1970-01-02"
    ).model_dump()

    rsp = client.put(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}', json=payload)
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["points"] == 5
    assert rsp.json["description"] == "updated"
    assert rsp.json["finished_at"] == "1970-01-02"


def test_delete_task_not_found(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = None

    rsp = client.delete(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_delete_task_ok(client: FlaskClient, mock_repos):
    _, _, participation, season = _wire_targets(mock_repos)

    t = Task(participation=participation, season=season, **base_task)
    mock_repos["task_repo"].get_task_by_participation_and_season.return_value = t
    mock_repos["task_repo"].delete_task.return_value = 123

    rsp = client.delete(f'/tasks/{base_member["username"]}/{base_project["name"]}/{base_season["season_number"]}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["id"] == 123
    assert "description" in rsp.json
