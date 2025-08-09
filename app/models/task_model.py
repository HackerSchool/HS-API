import re
from typing import List, TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.extensions import db
from app.utils import is_valid_datestring, PointTypeEnum

if TYPE_CHECKING:
    from app.schemas.task_schema import TaskSchema
    from app.models.project_participation_model import ProjectParticipation
    from app.models.season_model import Season


class Task(db.Model):
    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint("participation_id", "season_id", name="uq_task_participation_season"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    
    point_type: Mapped[PointTypeEnum] = mapped_column(Enum(PointTypeEnum, native_enum=False))
    points: Mapped[int] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    finished_at: Mapped[str] = mapped_column(nullable=True)

    participation_id: Mapped[int] = mapped_column(ForeignKey("project_participations.id"))
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), unique=True)
    participation: Mapped["ProjectParticipation"] = relationship("ProjectParticipation", back_populates="tasks")
    season: Mapped["Season"] = relationship("Season", back_populates="task", uselist=False)

    @classmethod
    def from_schema(cls, *, season: "Season", participation: "ProjectParticipation", schema: "TaskSchema"):
        return cls(season=season, participation=participation, 
                **schema.model_dump(exclude=["username", "project_name", "season_number"]))

    def __init__(self, *, season: "Season", participation: "ProjectParticipation", point_type: None, points: None, 
                description: None, finished_at: None):
        self.season = season
        self.participation = participation
        self.point_type = point_type
        self.points = points
        self.description = description
        self.finished_at = finished_at


    @validates("point_type")
    def validate_state(self, k, v):
        if not isinstance(v, PointTypeEnum):
            raise ValueError(f'Invalid point_typee: "{type(v)}"')
        return v

    @validates("points")
    def validate_points(self, k, v):
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError(f'Invalid points type: "{type(v)}"')
        if v < 1:
            raise ValueError(f"Invalid points, expected integer greater than 0: Got {v}")
        return v

    @validates("finished_at")
    def validate_datestring(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid {k} type: "{type(v)}"')
        if not is_valid_datestring(v):
            raise ValueError(f'Invalid {k} format, expected "YYYY-MM-DD": "{v}"')
        return v

    @validates("description")
    def validate_description(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid {k} type: "{type(v)}"')
        if len(v) > 2048:
            raise ValueError(f'Invalid {k} length, minimum 0 and maximum 2048 characters: "{v}"')
        return v

    def __repr__(self):
        return f"<{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})>"
