from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import delete, select

from app.models.team_task_model import TeamTask
from app.schemas.update_team_task_schema import UpdateTeamTaskSchema


class TeamTaskRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_task(self, task: TeamTask) -> TeamTask:
        self.db.session.add(task)
        return task

    def get_tasks(self) -> List[TeamTask]:
        return self.db.session.execute(select(TeamTask)).scalars().fetchall()

    def get_task_by_id(self, task_id: int) -> Optional[TeamTask]:
        return self.db.session.execute(
            select(TeamTask).where(TeamTask.id == task_id)
        ).scalars().one_or_none()

    def update_task(self, task: TeamTask, update_values: UpdateTeamTaskSchema) -> TeamTask:
        for key, value in update_values.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        return task

    def delete_task(self, task: TeamTask) -> int:
        self.db.session.execute(delete(TeamTask).where(TeamTask.id == task.id))
        return task.id

