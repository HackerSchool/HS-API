from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.utils import is_valid_datestring
from app.utils import ProjectStateEnum

from app.models.project_participation_model import ProjectParticipation

class ProjectParticipationSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern="^[a-zA-Z0-9]*$")
    join_date: str = Field(default=None)
    project_name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    roles: Optional[List[str]] = Field(default=None)

    @field_validator("join_date")
    @classmethod
    def validate_datestring(cls, v: str):
        if not is_valid_datestring(v):
            raise ValueError(
                f'Invalid date format: "{v}". Expected format is "YYYY-MM-DD"'
            )
        return v

    @classmethod
    def from_participation(cls, participation: ProjectParticipation):
        participation_data = {
            "username": participation.member.username,
            "project_name": participation.project.name
        }
        for field in {*cls.model_fields.keys()} - {"username", "project_name"}:
            if hasattr(participation, field):
                participation_data[field] = getattr(participation, field)
        return cls(**participation_data)

