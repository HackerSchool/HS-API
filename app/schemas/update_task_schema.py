from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.utils import is_valid_datestring, PointTypeEnum
from app.models.task_model import Task


class UpdateTaskSchema(BaseModel):
    point_type: Optional[PointTypeEnum] = Field(default=None)
    points: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
    finished_at: Optional[str] = Field(default=None)

    username: Optional[str] = Field(default=None, min_length=3, max_length=32, pattern="^[a-zA-Z0-9]*$")
    project_name: Optional[str] = Field(default=None)
    season_number: Optional[int] = Field(default=None, gt=0)

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

    @field_validator("points")
    @classmethod
    def validate_points(cls, v: Optional[int]):
        if v is None:
            return None
        if v == 0:
            raise ValueError("Invalid points, expected non-zero integer")
        return v

    @classmethod
    def from_task(cls, task: Task):
        data = {"point_type": task.point_type, "points": task.points, "description": task.description,
        "finished_at": task.finished_at, "username": task.participation.member.username, 
        "project_name": task.participation.project.name, "season_number": task.season.number}
        
        return cls(**data)

