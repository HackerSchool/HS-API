from app.models.task_model import Task
from app.models.project_participation_model import ProjectParticipation
from app.schemas.update_task_schema import UpdateTaskSchema

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete
from typing import List


class TaskRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_task(self, task: Task) -> Task:
        self.db.session.add(task)
        return task

    def get_tasks(self) -> List[Task]:
        return self.db.session.execute(select(Task)).scalars().fetchall()

    def get_tasks_by_season(self, season_id: int) -> List[Task]:
        return self.db.session.execute(
            select(Task).where(Task.season_id == season_id)
        ).scalars().fetchall()

    def get_tasks_by_member(self, member_id: int) -> List[Task]:
        return self.db.session.execute(
            select(Task)
            .join(ProjectParticipation)
            .where(ProjectParticipation.member_id == member_id)
        ).scalars().fetchall()

    def get_tasks_by_project(self, project_id: int) -> List[Task]:
        return self.db.session.execute(
            select(Task)
            .join(ProjectParticipation)
            .where(ProjectParticipation.project_id == project_id)
        ).scalars().fetchall()

    def get_tasks_by_member_and_season(self, member_id: int, season_id: int) -> List[Task]:
        return self.db.session.execute(
            select(Task)
            .join(ProjectParticipation)
            .where(
                ProjectParticipation.member_id == member_id,
                Task.season_id == season_id
            )
        ).scalars().fetchall()

    def get_tasks_by_project_and_season(self, project_id: int, season_id: int) -> List[Task]:
        return self.db.session.execute(
            select(Task)
            .join(ProjectParticipation)
            .where(
                ProjectParticipation.project_id == project_id,
                Task.season_id == season_id
            )
        ).scalars().fetchall()

    def get_task_by_participation_and_season(self, participation_id: int, season_id: int) -> Task | None:
        return self.db.session.execute(
            select(Task).where(
                Task.participation_id == participation_id,
                Task.season_id == season_id
            )
        ).scalars().one_or_none()

    def get_task_by_id(self, id: int) -> Task | None:
        return self.db.session.execute(
            select(Task).where(Task.id == id)
        ).scalars().one_or_none()

    def update_task(self, task: Task, update_values: UpdateTaskSchema) -> Task:
        for k, v in update_values.model_dump(exclude_unset=True).items():
            setattr(task, k, v)
        return task

    def delete_task(self, task: Task) -> int:
        self.db.session.execute(delete(Task).where(Task.id == task.id))
        return task.id
