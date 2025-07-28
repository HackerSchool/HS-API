from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils import is_valid_datestring
from app.models.project_model import Project

from app.utils import ProjectStateEnum

class UpdateProjectSchema(BaseModel):
    name: Optional[str] = Field(default=None)
    state: Optional[ProjectStateEnum] = Field(default=None)
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_datestring(cls, v: str):
        if v is None:
            return None
        if not is_valid_datestring(v):
            raise ValueError(
                f'Invalid date format: "{v}". Expected format is "YYYY-MM-DD"'
            )
        return v
