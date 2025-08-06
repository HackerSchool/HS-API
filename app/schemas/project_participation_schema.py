from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from app.utils import is_valid_datestring
from app.utils import ProjectStateEnum

from app.models.project_participation_model import ProjectParticipation

class ProjectParticipationSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern="^[a-zA-Z0-9]*$")
    project_name: str = Field(..., min_length=2, max_length=255)
    roles: List[str] = Field(default=[])
    join_date: str = Field(default=None)

    @field_validator("join_date")
    @classmethod
    def validate_datestring(cls, v: str):
        if not is_valid_datestring(v):
            raise ValueError(
                f'Invalid date format: "{v}". Expected format is "YYYY-MM-DD"'
            )
        return v

    @classmethod
    def from_pp(cls, pp: ProjectParticipation):
        pp_data = {
            "username": pp.member.username,
            "project_name": pp.project.name
        }
        for field in {cls.model_fields} - {"username", "project_name"}:
            if hasattr(pp, field):
                pp_data[field] = getattr(pp, field)
        return cls(**pp_data)

