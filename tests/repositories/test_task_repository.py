import pytest
from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db

from app.utils import ProjectStateEnum, PointTypeEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.project_participation_model import ProjectParticipation
from app.models.task_model import Task

from app.schemas.update_task_schema import UpdateTaskSchema
from app.repositories.task_repository import TaskRepository


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
def task_repo():
    return TaskRepository(db=db)


@pytest.fixture
def member():
    return Member(**base_member)


@pytest.fixture
def project():
    return Project(**base_project)


@pytest.fixture
def participation(member, project):
    return ProjectParticipation(member=member, project=project, **base_participation)


def add_task(*, participation):
    data = {**base_task}
    t = Task(participation=participation, **data)
    db.session.add(t)
    return t


def test_create_task(app, task_repo: TaskRepository, participation):
    task = Task(participation=participation, **base_task)
    task_repo.create_task(task)
    db.session.flush()

    gotten = db.session.execute(select(Task).where(Task.id == task.id)).scalars().one_or_none()
    assert gotten is not None
    assert gotten.point_type == base_task["point_type"]
    assert gotten.points == base_task["points"]
    assert gotten.description == base_task["description"]
    assert gotten.participation == participation


def test_get_tasks(app, task_repo: TaskRepository, participation):
    t1 = add_task(participation=participation)
    t2 = add_task(participation=participation)
    t3 = add_task(participation=participation)
    db.session.flush()

    tasks = task_repo.get_tasks()
    ids = {t.id for t in tasks}
    assert {t1.id, t2.id, t3.id}.issubset(ids)

def test_get_task_by_id(app, task_repo: TaskRepository, participation):
    t = add_task(participation=participation)
    db.session.flush()

    gotten = task_repo.get_task_by_id(t.id)
    assert gotten is not None
    assert gotten.description == t.description


def test_update_task(app, task_repo: TaskRepository, participation):
    t = add_task(participation=participation)
    db.session.flush()

    update_values = UpdateTaskSchema(point_type=PointTypeEnum.PCC, points=5, description="updated", finished_at="1970-01-02")
    updated = task_repo.update_task(t, update_values)

    gotten = db.session.execute(select(Task).where(Task.id == t.id)).scalars().one_or_none()
    assert gotten is not None
    assert gotten.points == updated.points == 5
    assert gotten.description == updated.description == "updated"
    assert gotten.finished_at == updated.finished_at == "1970-01-02"


def test_delete_task(app, task_repo: TaskRepository, participation):
    t = add_task(participation=participation)
    db.session.flush()

    deleted_id = task_repo.delete_task(t)
    assert deleted_id == t.id
    assert db.session.execute(select(Task).where(Task.id == t.id)).scalars().one_or_none() is None
