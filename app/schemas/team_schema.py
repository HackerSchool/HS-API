from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.utils import is_valid_datestring
from app.models.member_model import Member


class TeamSchema(BaseModel):
    

    username: str = Field(..., min_length=3, max_length=32, pattern="^[a-zA-Z0-9]*$")
    ist_id: Optional[str] = Field(default=None, pattern="^ist1[0-9]{5,7}$")
    name: str = Field(..., min_length=1, max_length=512)
    email: str = Field(..., min_length=1, max_length=512)

    password: Optional[str] = Field(default=None, min_length=6, max_length=256)
    member_number: Optional[int] = Field(default=None, gt=0)
    course: Optional[str] = Field(default=None, min_length=1, max_length=8)
    roles: Optional[List[str]] = Field(default=None)
    join_date: Optional[str] = Field(default=None)
    exit_date: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None, max_length=2048)
    extra: Optional[str] = Field(default=None, max_length=2048)

    @field_validator("join_date", "exit_date")
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
    def from_member(cls, member: Member):
        member_data = {}
        for field in cls.model_fields:
            if hasattr(member, field):
                member_data[field] = getattr(member, field)
        return cls(**member_data)

    def model_dump(self, *args, **kwargs):
        return super().model_dump(*args, **kwargs, exclude="password")
