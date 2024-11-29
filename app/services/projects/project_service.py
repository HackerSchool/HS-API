# project.py
from typing import List

from app.extensions import db
from app.models import Project, ProjectParticipation, User


def get_all_projects() -> List[Project]:
    """Returns a list of all projects"""
    return [project for project in Project.query.all()]


def get_project_by_name(name: str) -> Project | None:
    """Returns project with given `name` or None if project doesn't exist."""
    return Project.query.filter_by(name=name).one_or_none()


def delete_project(project: Project) -> int:
    """Deletes given `project` from the DB and returns project's username."""
    db.session.delete(project)
    db.session.commit()
    return project.name


def edit_project(project: Project, **kwargs) -> Project:
    """
    Edit given `project` with provided information.
    Returns updated project.
    """
    for field, val in kwargs.items():
        setattr(project, field, val)
    project.check_invariants()  # this will fail if the fields are invalid
    db.session.commit()
    return project


def create_project(
    name: str,
    start_date: str,
    state: str,
    description: str = "",
) -> Project:
    new_project = Project(name=name, start_date=start_date, state=state, description=description)
    db.session.add(new_project)
    db.session.commit()
    return new_project


def add_user_to_project(
    user: User,
    project: Project,
    entry_date: str,
) -> ProjectParticipation:
    """
    Add user to project and returns newly created Participation.
    If user is already associated with project returns None.
    """
    participation = ProjectParticipation(
        entry_date=entry_date,
        roles=["participant"],
        contributions="",
        exit_date="",
    )
    if (
        ProjectParticipation.query.filter_by(member_username=user.username, project_name=project.name).one_or_none()
        is not None
    ):
        return None

    participation.user = user
    project.participations.append(participation)
    db.session.add(participation)
    db.session.commit()
    return participation


def remove_user_from_project(
    user: User,
    project: Project,
) -> ProjectParticipation | None:
    """
    Remove user from project and returns newly created Participation.
    If user is not associated with project retursn None.
    """
    participation = ProjectParticipation.query.filter_by(
        member_username=user.username,
        project_name=project.name,
    ).one_or_none()
    if participation is None:
        return None

    db.session.delete(participation)
    db.session.commit()

    return participation


def get_project_user_roles(
    username: str,
    proj_name: str,
) -> List[str]:
    participation = ProjectParticipation.query.filter_by(member_username=username, project_name=proj_name).one_or_none()
    if participation is None:
        return []

    return participation.roles
