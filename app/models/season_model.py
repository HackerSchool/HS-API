import re
from typing import List, TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.extensions import db
from app.utils import is_valid_datestring

if TYPE_CHECKING:
    from app.schemas.season_schema import SeasonSchema
    from app.models.task_model import Task


class Season(db.Model):
    __tablename__ = "seasons"
    __table_args__ = (
        CheckConstraint("start_date <= end_date", name="ck_season_dates"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    season_number: Mapped[int] = mapped_column(unique=True, nullable=True)
    start_date: Mapped[str] = mapped_column(nullable=True)
    end_date: Mapped[str] = mapped_column(nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="season")

    @classmethod
    def from_schema(cls, *, schema: "SeasonSchema"):
        return cls(**schema.model_dump())

    def __init__(self, *, season_number=None, start_date=None, end_date=None):
        self.season_number = season_number
        self.start_date = start_date
        self.end_date = end_date

    @validates("season_number")
    def validate_season_number(self, k, v):
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError(f'Invalid season_number type: "{type(v)}"')
        if v < 1:
            raise ValueError(f"Invalid season_number, expected integer greater than 0: Got {v}")
        return v

    @validates("start_date", "end_date")
    def validate_datestring(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid {k} type: "{type(v)}"')
        if not is_valid_datestring(v):
            raise ValueError(f'Invalid {k} format, expected "YYYY-MM-DD": "{v}"')
        return v

    def __repr__(self):
        return f"<{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})>"
