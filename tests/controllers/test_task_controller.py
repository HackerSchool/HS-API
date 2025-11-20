from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from flask.testing import FlaskClient

from app import create_app
from app.models.member_model import Member
from app.models.project_model import Project
from app.models.project_participation_model import ProjectParticipation
from app.models.task_model import Task
from app.models.team_task_model import TeamTask
from app.schemas.task_schema import TaskSchema
from app.schemas.team_task_schema import TeamTaskSchema
from app.schemas.update_task_schema import UpdateTaskSchema
from app.schemas.update_team_task_schema import UpdateTeamTaskSchema
from app.utils import ProjectStateEnum, PointTypeEnum

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


base_task = {
    "point_type": PointTypeEnum.PJ,
    "points": 1,
    "description": "description",
    "finished_at": None,
}

payload_create = {
    "username": base_member["username"],
    "project_name": base_project["name"],
    "point_type": base_task["point_type"],
    "points": base_task["points"],
    "description": base_task["description"],
    "finished_at": base_task["finished_at"],
}

base_team_task = {
    "point_type": PointTypeEnum.PJ,
    "points": 10,
    "description": "Team description",
    "finished_at": None,
    "contributors": ["username", "alex"],
}

payload_team_task_create = {
    "point_type": base_team_task["point_type"],
    "points": base_team_task["points"],
    "description": base_team_task["description"],
    "finished_at": base_team_task["finished_at"],
    "contributors": base_team_task["contributors"],
}


@pytest.fixture
def mock_repos():
    return {
        "task_repo": MagicMock(),
        "team_task_repo": MagicMock(),
        "member_repo": MagicMock(),
        "project_repo": MagicMock(),
        "participation_repo": MagicMock(),
    }


@pytest.fixture
def client(mock_repos):
    from app.config import Config
    Config.ENABLED_ACCESS_CONTROL = False

    app = create_app(
        task_repo=mock_repos["task_repo"],
        team_task_repo=mock_repos["team_task_repo"],
        member_repo=mock_repos["member_repo"],
        project_repo=mock_repos["project_repo"],
        participation_repo=mock_repos["participation_repo"],
    )
    with app.test_client() as client:
        yield client


def _wire_targets(mock_repos):
    member = Member(**base_member)
    project = Project(**base_project)
    participation = ProjectParticipation(member=member, project=project, **base_participation)

    mock_repos["member_repo"].get_member_by_username.return_value = member
    mock_repos["project_repo"].get_project_by_slug.return_value = project
    mock_repos["participation_repo"].get_participation_by_project_and_member_id.return_value = participation

    return member, project, participation


def test_create_task_ok(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)

    created = Task(participation=participation, **base_task)
    mock_repos["task_repo"].create_task.return_value = created

    rsp = client.post(f"/projects/{created.participation.project.slug}/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["username"] == payload_create["username"]
    assert rsp.json["project_name"] == payload_create["project_name"]
    assert rsp.json["point_type"] == payload_create["point_type"]
    assert rsp.json["points"] == payload_create["points"]
    assert rsp.json["description"] == payload_create["description"]
    assert rsp.json["finished_at"] == payload_create["finished_at"]


def test_create_task_member_not_found(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)
    mock_repos["member_repo"].get_member_by_username.return_value = None

    rsp = client.post(f"/projects/{participation.project.slug}/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_create_task_project_not_found(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)
    mock_repos["member_repo"].get_member_by_username.return_value = object()
    mock_repos["project_repo"].get_project_by_slug.return_value = None


    rsp = client.post("/projects/no-exist/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_create_task_participation_not_found(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_slug.return_value = Project(**base_project)
    mock_repos["participation_repo"].get_participation_by_project_and_member_id.return_value = None

    rsp = client.post(f"/projects/{participation.project.slug}/tasks", json=TaskSchema(**payload_create).model_dump())
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_by_id_ok(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)

    t = Task(participation=participation, **base_task)
    t.id = 1
    mock_repos["task_repo"].get_task_by_id.return_value = t

    rsp = client.get(f"/tasks/{t.id}")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["username"] == base_member["username"]
    assert rsp.json["project_name"] == base_project["name"]


def test_get_task_by_id_not_found(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_id.return_value = None

    rsp = client.get(f'/tasks/1')
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_get_task_by_member_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = None
    rsp = client.get(f'/members/username/tasks')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_by_project_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_slug.return_value = None
    rsp = client.get(f'/projects/slug/tasks')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_task_participation_not_found(client: FlaskClient, mock_repos):
    mock_repos["member_repo"].get_member_by_username.return_value = Member(**base_member)
    mock_repos["project_repo"].get_project_by_slug.return_value = Project(**base_project)
    mock_repos["participation_repo"].get_participation_by_project_and_member_id.return_value = None
    rsp = client.get(f'/tasks/')
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_update_task_not_found(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_id.return_value = None

    payload = UpdateTaskSchema(
        point_type=PointTypeEnum.PJ, points=2, description="upd", finished_at="1970-01-02"
    ).model_dump()
    rsp = client.put(f'/tasks/10', json=payload)
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_update_task_ok(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)

    current = Task(participation=participation, **base_task)
    current.id = 1
    updated = Task(
        participation=participation, point_type=PointTypeEnum.PJ, points=5, description="updated", finished_at="1970-01-02"
    )
    updated.id = 1

    mock_repos["task_repo"].get_task_by_id.return_value = current
    mock_repos["task_repo"].update_task.return_value = updated

    payload = UpdateTaskSchema(
        point_type=PointTypeEnum.PJ, points=5, description="updated", finished_at="1970-01-02"
    ).model_dump()

    rsp = client.put(f'/tasks/{current.id}', json=payload)
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["points"] == 5
    assert rsp.json["description"] == "updated"
    assert rsp.json["finished_at"] == "1970-01-02"


def test_delete_task_not_found(client: FlaskClient, mock_repos):
    _wire_targets(mock_repos)
    mock_repos["task_repo"].get_task_by_id.return_value = None

    rsp = client.delete(f'/tasks/1')
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_delete_task_by_id_ok(client: FlaskClient, mock_repos):
    _, _, participation = _wire_targets(mock_repos)

    t = Task(participation=participation, **base_task)
    t.id = 1
    mock_repos["task_repo"].get_task_by_id.return_value = t
    mock_repos["task_repo"].delete_task.return_value = t.id

    rsp = client.delete(f'/tasks/{t.id}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["id"] == t.id
    assert "description" in rsp.json


def test_create_team_task_ok(client: FlaskClient, mock_repos):
    _, project, _ = _wire_targets(mock_repos)
    created = TeamTask(project=project, **base_team_task)
    mock_repos["team_task_repo"].create_task.return_value = created

    rsp = client.post(
        f"/projects/{project.slug}/team-tasks",
        json=TeamTaskSchema(**payload_team_task_create).model_dump(),
    )
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["point_type"] == payload_team_task_create["point_type"]
    assert rsp.json["points"] == payload_team_task_create["points"]
    assert rsp.json["description"] == payload_team_task_create["description"]
    assert rsp.json["contributors"] == payload_team_task_create["contributors"]


def test_create_team_task_project_not_found(client: FlaskClient, mock_repos):
    mock_repos["project_repo"].get_project_by_slug.return_value = None
    rsp = client.post(
        "/projects/slug/team-tasks",
        json=TeamTaskSchema(**payload_team_task_create).model_dump(),
    )
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_project_team_tasks_ok(client: FlaskClient, mock_repos):
    _, project, _ = _wire_targets(mock_repos)
    task = TeamTask(project=project, **base_team_task)
    project.team_tasks = [task]

    rsp = client.get(f"/projects/{project.slug}/team-tasks")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert len(rsp.json) == 1
    assert rsp.json[0]["points"] == base_team_task["points"]
    assert rsp.json[0]["contributors"] == base_team_task["contributors"]


def test_get_project_team_tasks_project_not_found(client: FlaskClient, mock_repos):
    mock_repos["project_repo"].get_project_by_slug.return_value = None
    rsp = client.get("/projects/slug/team-tasks")
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_get_team_task_by_id_ok(client: FlaskClient, mock_repos):
    _, project, _ = _wire_targets(mock_repos)
    task = TeamTask(project=project, **base_team_task)
    task.id = 5
    mock_repos["team_task_repo"].get_task_by_id.return_value = task

    rsp = client.get(f"/team-tasks/{task.id}")
    assert rsp.status_code == 200
    assert rsp.json["id"] == task.id
    assert rsp.json["points"] == base_team_task["points"]
    assert rsp.json["contributors"] == base_team_task["contributors"]


def test_get_team_task_by_id_not_found(client: FlaskClient, mock_repos):
    mock_repos["team_task_repo"].get_task_by_id.return_value = None
    rsp = client.get("/team-tasks/1")
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_update_team_task_ok(client: FlaskClient, mock_repos):
    _, project, _ = _wire_targets(mock_repos)
    task = TeamTask(project=project, **base_team_task)
    task.id = 1
    updated = TeamTask(
        project=project,
        point_type=PointTypeEnum.PCC,
        points=20,
        description="updated",
        finished_at="1970-01-02",
        contributors=["username"],
    )
    updated.id = task.id

    mock_repos["team_task_repo"].get_task_by_id.return_value = task
    mock_repos["team_task_repo"].update_task.return_value = updated

    payload = UpdateTeamTaskSchema(
        point_type=PointTypeEnum.PCC,
        points=20,
        description="updated",
        finished_at="1970-01-02",
        contributors=["username"],
    ).model_dump()

    rsp = client.put(f"/team-tasks/{task.id}", json=payload)
    assert rsp.status_code == 200
    assert rsp.json["points"] == 20
    assert rsp.json["description"] == "updated"
    assert rsp.json["finished_at"] == "1970-01-02"
    assert rsp.json["contributors"] == ["username"]


def test_update_team_task_not_found(client: FlaskClient, mock_repos):
    mock_repos["team_task_repo"].get_task_by_id.return_value = None
    payload = UpdateTeamTaskSchema(points=10, contributors=["username"]).model_dump()
    rsp = client.put("/team-tasks/1", json=payload)
    assert rsp.status_code == HTTPStatus.NOT_FOUND


def test_delete_team_task_ok(client: FlaskClient, mock_repos):
    _, project, _ = _wire_targets(mock_repos)
    task = TeamTask(project=project, **base_team_task)
    task.id = 1

    mock_repos["team_task_repo"].get_task_by_id.return_value = task
    mock_repos["team_task_repo"].delete_task.return_value = task.id

    rsp = client.delete(f"/team-tasks/{task.id}")
    assert rsp.status_code == 200
    assert rsp.json["id"] == task.id


def test_delete_team_task_not_found(client: FlaskClient, mock_repos):
    mock_repos["team_task_repo"].get_task_by_id.return_value = None
    rsp = client.delete("/team-tasks/1")
    assert rsp.status_code == HTTPStatus.NOT_FOUND
