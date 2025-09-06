from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload

from app.models.project_participation_model import ProjectParticipation
from app.models.task_model import Task
from app.schemas.update_task_schema import UpdateTaskSchema


class TaskRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_task(self, task: Task) -> Task:
        self.db.session.add(task)
        return task

    def get_tasks(self) -> List[Task]:
        return self.db.session.execute(select(Task)).scalars().fetchall()

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
