import pytest
from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db

from app.utils import ProjectStateEnum, PointTypeEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.season_model import Season
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
def season():
    return Season(season_number=1, start_date="1970-01-01", end_date="1970-12-31")


@pytest.fixture
def participation(member, project):
    return ProjectParticipation(member=member, project=project, **base_participation)


def add_task(*, participation, season):
    data = {**base_task}
    t = Task(participation=participation, season=season, **data)
    db.session.add(t)
    return t


def test_create_task(app, task_repo: TaskRepository, participation, season):
    task = Task(participation=participation, season=season, **base_task)
    task_repo.create_task(task)
    db.session.flush()

    gotten = db.session.execute(select(Task).where(Task.id == task.id)).scalars().one_or_none()
    assert gotten is not None
    assert gotten.point_type == base_task["point_type"]
    assert gotten.points == base_task["points"]
    assert gotten.description == base_task["description"]
    assert gotten.participation == participation
    assert gotten.season == season


def test_get_tasks(app, task_repo: TaskRepository, participation):

    s1 = Season(season_number=1, start_date="1970-01-01", end_date="1970-12-31")
    s2 = Season(season_number=2, start_date="1971-01-01", end_date="1971-12-31")
    s3 = Season(season_number=3, start_date="1972-01-01", end_date="1972-12-31")
    db.session.add_all([s1, s2, s3])

    t1 = add_task(participation=participation, season=s1)
    t2 = add_task(participation=participation, season=s2)
    t3 = add_task(participation=participation, season=s3)
    db.session.flush()

    tasks = task_repo.get_tasks()
    ids = {t.id for t in tasks}
    assert {t1.id, t2.id, t3.id}.issubset(ids)


def test_get_tasks_by_season(app, task_repo: TaskRepository, participation):
    s = Season(season_number=10, start_date="1980-01-01", end_date="1980-12-31")
    db.session.add(s)
    t = add_task(participation=participation, season=s)
    db.session.flush()

    tasks = task_repo.get_tasks_by_season(s.id)
    assert len(tasks) == 1
    assert tasks[0].id == t.id


def test_get_tasks_by_member(app, task_repo: TaskRepository, project, season):
    m1 = Member(**base_member)
    m2 = Member(**{**base_member, "username": "username2", "email": "email2"})
    db.session.add_all([m1, m2])

    p1 = ProjectParticipation(member=m1, project=project, **base_participation)
    p2 = ProjectParticipation(member=m2, project=project, **base_participation)
    s1 = season
    s2 = Season(season_number=2, start_date="1971-01-01", end_date="1971-12-31")
    db.session.add_all([p1, p2, s1, s2])

    t1 = add_task(participation=p1, season=s1)
    t2 = add_task(participation=p1, season=s2)
    _ = add_task(participation=p2, season=Season(season_number=3, start_date="1972-01-01", end_date="1972-12-31"))
    db.session.flush()

    tasks = task_repo.get_tasks_by_member(m1.id)
    assert {t.id for t in tasks} == {t1.id, t2.id}


def test_get_tasks_by_project(app, task_repo: TaskRepository, member, season):
    p1 = Project(**base_project)
    p2 = Project(**{**base_project, "name": "proj_other"})
    db.session.add_all([p1, p2])

    part1 = ProjectParticipation(member=member, project=p1, **base_participation)
    part2 = ProjectParticipation(member=member, project=p2, **base_participation)
    s1 = season
    s2 = Season(season_number=2, start_date="1971-01-01", end_date="1971-12-31")
    db.session.add_all([part1, part2, s1, s2])

    t1 = add_task(participation=part1, season=s1)
    t2 = add_task(participation=part1, season=s2)
    _ = add_task(participation=part2, season=Season(season_number=3, start_date="1972-01-01", end_date="1972-12-31"))
    db.session.flush()

    tasks = task_repo.get_tasks_by_project(p1.id)
    assert {t.id for t in tasks} == {t1.id, t2.id}


def test_get_tasks_by_member_and_season(app, task_repo: TaskRepository, project):
    m = Member(**base_member)
    db.session.add(m)
    part = ProjectParticipation(member=m, project=project, **base_participation)
    s = Season(season_number=10, start_date="1980-01-01", end_date="1980-12-31")
    db.session.add_all([part, s])

    t = add_task(participation=part, season=s)
    db.session.flush()

    tasks = task_repo.get_tasks_by_member_and_season(member_id=m.id, season_id=s.id)
    assert len(tasks) == 1
    assert tasks[0].id == t.id


def test_get_tasks_by_project_and_season(app, task_repo: TaskRepository, member):
    p = Project(**base_project)
    db.session.add(p)
    part = ProjectParticipation(member=member, project=p, **base_participation)
    s = Season(season_number=20, start_date="1990-01-01", end_date="1990-12-31")
    db.session.add_all([part, s])

    t = add_task(participation=part, season=s)
    db.session.flush()

    tasks = task_repo.get_tasks_by_project_and_season(project_id=p.id, season_id=s.id)
    assert len(tasks) == 1
    assert tasks[0].id == t.id


def test_get_task_by_participation_and_season(app, task_repo: TaskRepository, member, project):
    part = ProjectParticipation(member=member, project=project, **base_participation)
    s = Season(season_number=30, start_date="2000-01-01", end_date="2000-12-31")
    db.session.add_all([part, s])

    t = add_task(participation=part, season=s)
    db.session.flush()

    gotten = task_repo.get_task_by_participation_and_season(participation_id=part.id, season_id=s.id)
    assert gotten is not None
    assert gotten.id == t.id


def test_get_task_by_id(app, task_repo: TaskRepository, participation, season):
    t = add_task(participation=participation, season=season)
    db.session.flush()

    gotten = task_repo.get_task_by_id(t.id)
    assert gotten is not None
    assert gotten.description == t.description


def test_update_task(app, task_repo: TaskRepository, participation, season):
    t = add_task(participation=participation, season=season)
    db.session.flush()

    update_values = UpdateTaskSchema(point_type=PointTypeEnum.PCC, points=5, description="updated", finished_at="1970-01-02")
    updated = task_repo.update_task(t, update_values)

    gotten = db.session.execute(select(Task).where(Task.id == t.id)).scalars().one_or_none()
    assert gotten is not None
    assert gotten.points == updated.points == 5
    assert gotten.description == updated.description == "updated"
    assert gotten.finished_at == updated.finished_at == "1970-01-02"


def test_delete_task(app, task_repo: TaskRepository, participation, season):
    t = add_task(participation=participation, season=season)
    db.session.flush()

    deleted_id = task_repo.delete_task(t)
    assert deleted_id == t.id
    assert db.session.execute(select(Task).where(Task.id == t.id)).scalars().one_or_none() is None
