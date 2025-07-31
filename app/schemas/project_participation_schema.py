from typing import Optional, List

from pydantic import BaseModel, Field

class ProjectParticipationSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, pattern="^[a-zA-Z0-9]*$")
    project_name: str = Field(..., min_length=2, max_length=255)
    join_date: str = Field(...)
    roles: List[str] = Field(default=[])

    end_date: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=2048)


