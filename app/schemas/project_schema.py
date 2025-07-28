from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils import is_valid_datestring
from app.utils import ProjectStateEnum

from app.models.project_model import Project

class ProjectSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    state: ProjectStateEnum = Field(...)
    start_date: str = Field(...)

    slug: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    @classmethod
    @field_validator("start_date")
    def validate_datestring(cls, v: str):
        if v is None:
            raise None
        if not is_valid_datestring(v):
            raise ValueError(
                f'Invalid date format: "{v}". Expected format is "YYYY-MM-DD"'
            )
        return v

    @field_validator("end_date")
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
    def from_project(cls, project: Project):
        project_data = {}
        for field in cls.model_fields:
            if hasattr(project, field):
                project_data[field] = getattr(project, field)
        return cls(**project_data)


