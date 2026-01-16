from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.utils import is_valid_datestring, PointTypeEnum
from app.models.task_model import Task


class TaskSchema(BaseModel):
    id: Optional[int] = Field(None, gt=0)

    point_type: PointTypeEnum = Field(...)
    points: int = Field(default=None)
    description: str = Field(default=None)
    finished_at: Optional[str] = Field(default=None)

    username: str = Field(default=None, min_length=3, max_length=32, pattern="^[a-zA-Z0-9]*$")
    project_name: str = Field(default=None)

    @field_validator("finished_at")
    @classmethod
    def validate_datestring(cls, v: str):
        if v is None:
            return None
        if not is_valid_datestring(v):
            raise ValueError(
                f'Invalid date format: "{v}". Expected format is "YYYY-MM-DD"'
            )
        return v

    @classmethod
    def from_task(cls, task: Task):
        # All tasks now have participation (including "Contribuições Individuais")
        username = task.participation.member.username if task.participation else None
        project_name = task.participation.project.name if task.participation else None
        
        data = {
            "id": task.id,
            "point_type": task.point_type,
            "points": task.points,
            "description": task.description,
            "finished_at": task.finished_at,
            "username": username,
            "project_name": project_name,
        }
        return cls(**data)

