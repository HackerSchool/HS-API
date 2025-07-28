from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete

from typing import List

from app.models.project_model import Project
from app.schemas.update_project_schema import UpdateProjectSchema


class ProjectRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_project(self, project: Project):
        self.db.session.add(project)
        return project

    def get_projects(self) -> List[Project]:
        return self.db.session.execute(select(Project)).scalars().fetchall()

    def get_project_by_name(self, name: str) -> Project:
        # disadvantage of having our domain models coupled with sqlalchemy
        # with model properties sqlalchemy can't build the query on top of it...
        return self.db.session.execute(select(Project).where(Project._name == name)).scalars().one_or_none()

    def get_project_by_slug(self, slug: str) -> Project | None:
        return self.db.session.execute(select(Project).where(Project.slug == slug)).scalars().one_or_none()

    def update_project(self, project: Project, update_values: UpdateProjectSchema) -> Project:
        for k, v in update_values.model_dump(exclude_unset=True).items():
            setattr(project, k, v)
        return project

    def delete_project(self, project: Project) -> str:
        self.db.session.execute(delete(Project).where(Project.slug == project.slug))
        return project.name

