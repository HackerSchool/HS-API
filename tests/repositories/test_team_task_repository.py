import pytest
from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db

from app.models.project_model import Project
from app.models.team_task_model import TeamTask
from app.repositories.team_task_repository import TeamTaskRepository
from app.schemas.update_team_task_schema import UpdateTeamTaskSchema
from app.utils import PointTypeEnum, ProjectStateEnum


base_project = {
    "name": "proj_name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE,
}

base_team_task = {
    "point_type": PointTypeEnum.PJ,
    "points": 10,
    "description": "Team task description",
    "finished_at": None,
    "contributors": ["member1", "member2"],
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
def team_task_repo():
    return TeamTaskRepository(db=db)


@pytest.fixture
def project():
    return Project(**base_project)


def add_team_task(*, project):
    task = TeamTask(project=project, **base_team_task)
    db.session.add(project)
    db.session.add(task)
    return task


def test_create_team_task(app, team_task_repo: TeamTaskRepository, project):
    db.session.add(project)
    task = TeamTask(project=project, **base_team_task)
    team_task_repo.create_task(task)
    db.session.flush()

    gotten = db.session.execute(select(TeamTask).where(TeamTask.id == task.id)).scalars().one_or_none()
    assert gotten is not None
    assert gotten.points == base_team_task["points"]
    assert gotten.description == base_team_task["description"]
    assert gotten.contributors == base_team_task["contributors"]


def test_get_team_tasks(app, team_task_repo: TeamTaskRepository, project):
    t1 = add_team_task(project=project)
    t2 = add_team_task(project=project)
    db.session.flush()

    tasks = team_task_repo.get_tasks()
    ids = {t.id for t in tasks}
    assert {t1.id, t2.id}.issubset(ids)


def test_get_team_task_by_id(app, team_task_repo: TeamTaskRepository, project):
    t = add_team_task(project=project)
    db.session.flush()

    gotten = team_task_repo.get_task_by_id(t.id)
    assert gotten is not None
    assert gotten.points == base_team_task["points"]
    assert gotten.contributors == base_team_task["contributors"]


def test_update_team_task(app, team_task_repo: TeamTaskRepository, project):
    t = add_team_task(project=project)
    db.session.flush()

    update_values = UpdateTeamTaskSchema(
        point_type=PointTypeEnum.PCC,
        points=20,
        description="updated",
        finished_at="1970-01-02",
        contributors=["member1"],
    )
    updated = team_task_repo.update_task(t, update_values)

    gotten = db.session.execute(select(TeamTask).where(TeamTask.id == t.id)).scalars().one_or_none()
    assert gotten is not None
    assert gotten.points == updated.points == 20
    assert gotten.description == updated.description == "updated"
    assert gotten.finished_at == updated.finished_at == "1970-01-02"
    assert gotten.contributors == ["member1"]


def test_delete_team_task(app, team_task_repo: TeamTaskRepository, project):
    t = add_team_task(project=project)
    db.session.flush()

    deleted_id = team_task_repo.delete_task(t)
    assert deleted_id == t.id
    assert db.session.execute(select(TeamTask).where(TeamTask.id == t.id)).scalars().one_or_none() is None

