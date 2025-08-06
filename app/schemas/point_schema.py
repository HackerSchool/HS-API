from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.utils import is_valid_datestring
from app.utils import ProjectStateEnum

from app.models.project_model import ProjectParticipation

class PointSchema(BaseModel):
    member_id: int
    pj: Optional[int] = Field(default=None)
    pcc: Optional[List[str]] = Field(default=None)
    ps: Optional[List[str]] = Field(default=None)


    @classmethod
    def from_point(cls, pp: ProjectParticipation):
        data = {}
        for field in cls.model_fields:
            if hasattr(pp, field):
                data[field] = getattr(pp, field)
        return cls(**data)

