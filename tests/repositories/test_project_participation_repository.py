import pytest

from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db
from app.utils import ProjectStateEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.project_participation_model import ProjectParticipation

from app.schemas.update_project_participation_schema import UpdateProjectParticipationSchema

from app.repositories.project_participation_repository import ProjectParticipationRepository

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


@pytest.fixture(scope="function")
def app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    app = create_app()
    with app.app_context():
        db.create_all()
        yield
        db.session.commit()  # flush transactions or it won't be able to drop
        db.drop_all()


@pytest.fixture
def member():
    return Member(**base_member)


@pytest.fixture
def project():
    return Project(**base_project)


@pytest.fixture
def participation_repo():
    return ProjectParticipationRepository(db=db)


def test_create_participation(app, member, project, participation_repo: ProjectParticipationRepository):
    participation = ProjectParticipation(member=member, project=project, **base_participation)
    participation_repo.create_participation(participation)
    db.session.flush()
    gotten_participation = db.session.execute(
        select(ProjectParticipation).where(member.id == member.id, project.id == project.id)).scalars().one_or_none()
    assert gotten_participation is not None
    assert participation.join_date == gotten_participation.join_date
    assert participation.roles == gotten_participation.roles
    assert participation.member.id == gotten_participation.member.id
    assert participation.project.id == gotten_participation.project.id
    assert participation in member.project_participations
    assert participation in project.project_participations


def test_get_participations(app, project, participation_repo: ProjectParticipationRepository):
    members = []
    for i in range(3):
        mem = Member(**{**base_member, "username": "username" + str(i)})
        members.append(mem)
        db.session.add(ProjectParticipation(member=mem, project=project, **base_participation))
    db.session.flush()

    gotten_participations = participation_repo.get_participations()
    assert isinstance(gotten_participations, list)
    assert len(gotten_participations) == 3
    for p in gotten_participations:
        assert p.member in members
        assert p.project == project


def test_get_participation_by_project_and_member_id(app, member, project,
                                                    participation_repo: ProjectParticipationRepository):
    participation = ProjectParticipation(member=member, project=project, **base_participation)
    db.session.add(participation)
    db.session.flush()
    gotten_participation = participation_repo.get_participation_by_project_and_member_id(project_id=project.id,
                                                                                         member_id=member.id)

    assert gotten_participation is not None
    assert participation.join_date == gotten_participation.join_date
    assert gotten_participation.member == member
    assert gotten_participation.project == project


def test_update_participation(app, member, project, participation_repo: ProjectParticipationRepository):
    participation = ProjectParticipation(member=member, project=project, **base_participation)
    db.session.add(participation)
    db.session.flush()
    update_values = UpdateProjectParticipationSchema(roles=["coordinator"])
    participation_repo.update_participation(participation=participation, update_values=update_values)
    gotten_participation = db.session.execute(
        select(ProjectParticipation).where(ProjectParticipation.id == participation.id)).scalars().one_or_none()
    assert participation.join_date == gotten_participation.join_date
    assert update_values.roles == gotten_participation.roles


def test_delete_participation(app, member, project, participation_repo: ProjectParticipationRepository):
    participation = ProjectParticipation(member=member, project=project, **base_participation)
    db.session.add(participation)
    db.session.flush()
    username, project_name = participation_repo.delete_participation(participation)
    assert username == member.username
    assert project_name == project.name
    assert db.session.execute(
        select(ProjectParticipation).where(ProjectParticipation.id == participation.id)).scalars().one_or_none() is None

