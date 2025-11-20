from typing import TYPE_CHECKING, List

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.extensions import db
from app.utils import PointTypeEnum, is_valid_datestring

if TYPE_CHECKING:
    from app.models.project_model import Project
    from app.schemas.team_task_schema import TeamTaskSchema


class TeamTask(db.Model):
    __tablename__ = "team_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)

    point_type: Mapped[PointTypeEnum] = mapped_column(Enum(PointTypeEnum, native_enum=False), nullable=False)
    points: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    finished_at: Mapped[str] = mapped_column(nullable=True)
    _contributors: Mapped[str] = mapped_column("contributors", default="", nullable=False)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))

    project: Mapped["Project"] = relationship("Project", back_populates="team_tasks", lazy="joined")

    @classmethod
    def from_schema(cls, *, project: "Project", schema: "TeamTaskSchema"):
        return cls(
            project=project,
            **schema.model_dump(exclude={"id", "project_name"})
        )

    def __init__(self, *, project: "Project", point_type=None, points=None,
                 description=None, finished_at=None, contributors=None):
        self.project = project
        self.project_id = project.id
        self.point_type = point_type
        self.points = points
        self.description = description
        self.finished_at = finished_at
        self.contributors = contributors

    @validates("point_type")
    def validate_point_type(self, key, value):
        if not isinstance(value, PointTypeEnum):
            raise ValueError(f'Invalid point_typee: "{type(value)}"')
        return value

    @validates("points")
    def validate_points(self, key, value):
        if value is None:
            return None
        if not isinstance(value, int):
            raise ValueError(f'Invalid points type: "{type(value)}"')
        if value == 0:
            raise ValueError(f"Invalid points, expected non-zero integer: Got {value}")
        return value

    @validates("finished_at")
    def validate_datestring(self, key, value):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f'Invalid {key} type: "{type(value)}"')
        if not is_valid_datestring(value):
            raise ValueError(f'Invalid {key} format, expected "YYYY-MM-DD": "{value}"')
        return value

    @validates("description")
    def validate_description(self, key, value):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f'Invalid {key} type: "{type(value)}"')
        if len(value) > 2048:
            raise ValueError(f'Invalid {key} length, minimum 0 and maximum 2048 characters: "{value}"')
        return value

    @property
    def contributors(self) -> List[str]:
        if self._contributors == "":
            return []
        return self._contributors.split(",")

    @contributors.setter
    def contributors(self, value: List[str]):
        if value is None:
            self._contributors = ""
            return
        if not isinstance(value, list):
            raise ValueError(f'Invalid contributors type: "{type(value)}"')
        normalized = []
        for username in value:
            if not isinstance(username, str):
                raise ValueError(f'Invalid contributor username type: "{type(username)}"')
            if username == "":
                raise ValueError("Contributor usernames cannot be empty")
            normalized.append(username)
        self._contributors = ",".join(normalized)

    def __repr__(self):
        return f"<{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})>"

