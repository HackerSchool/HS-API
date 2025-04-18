# project.py
from typing import List

from app.extensions import db

from app.models import Project


def create_project(
    name: str,
    start_date: str,
    state: str,
    description: str = "",
):
    new_project = Project(
        name=name, start_date=start_date, state=state, description=description
    )
    db.session.add(new_project)
    db.session.commit()
    return new_project


def get_all_projects() -> List[Project]:
    """Returns a list of all projects"""
    return [project for project in Project.query.all()]


def get_project_by_name(name: str) -> Project:
    """Returns project with given `name` or None if project doesn't exist."""
    project = Project.query.filter_by(name=name).first()
    return project if project else None


def delete_project(project: Project) -> int:
    """Deletes given `rpoject` from the DB and returns project's username."""
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
