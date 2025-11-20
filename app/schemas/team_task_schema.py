from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.team_task_model import TeamTask
from app.utils import PointTypeEnum, is_valid_datestring


class TeamTaskSchema(BaseModel):
    id: Optional[int] = Field(None, gt=0)

    point_type: PointTypeEnum = Field(...)
    points: int = Field(default=None)
    description: Optional[str] = Field(default=None)
    finished_at: Optional[str] = Field(default=None)
    contributors: List[str] = Field(default_factory=list)

    project_name: Optional[str] = Field(default=None)

    @field_validator("finished_at")
    @classmethod
    def validate_datestring(cls, value: Optional[str]):
        if value is None:
            return None
        if not is_valid_datestring(value):
            raise ValueError(
                f'Invalid date format: "{value}". Expected format is "YYYY-MM-DD"'
            )
        return value

    @field_validator("contributors")
    @classmethod
    def validate_contributors(cls, value: List[str]):
        if value is None:
            return []
        normalized = []
        for username in value:
            if not isinstance(username, str):
                raise ValueError(f'Invalid contributor username type: "{type(username)}"')
            username = username.strip()
            if username == "":
                raise ValueError("Contributor usernames cannot be empty")
            normalized.append(username)
        return normalized

    @classmethod
    def from_task(cls, task: TeamTask):
        data = {
            "id": task.id,
            "point_type": task.point_type,
            "points": task.points,
            "description": task.description,
            "finished_at": task.finished_at,
            "contributors": task.contributors,
            "project_name": task.project.name,
        }
        return cls(**data)

