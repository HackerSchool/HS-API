from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.utils import is_valid_datestring
from app.models.season_model import Season


class SeasonSchema(BaseModel):
    season_number: int = Field(default=None, gt=0)
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)

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

    @classmethod
    def from_season(cls, season: Season):
        season_data = {}
        for field in cls.model_fields:
            if hasattr(season, field):
                season_data[field] = getattr(season, field)
        return cls(**season_data)

