import re
from typing import List, TYPE_CHECKING

import bcrypt
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.extensions import db
from app.utils import is_valid_datestring

if TYPE_CHECKING:
    from app.schemas.project_participation_schema import ProjectParticipationSchema
    from app.models.member_model import Member 
    from app.models.project_model import Project

class ProjectParticipation(db.Model):
    __tablename__ = "project_participation"
    __table_args__ = (
        UniqueConstraint("member_id", "project_id", name="uq_member_project"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    join_date: Mapped[str] = mapped_column(nullable=True)
    _roles: Mapped[str] = mapped_column("roles", nullable=True)

    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    member: Mapped["Member"] = relationship("Member", back_populates="project_participations")
    project: Mapped["Project"] = relationship("Project", back_populates="project_participations")


    """ @classmethod
    def from_schema(cls, schema: "ProjectParticipationSchema", member: "Member", project: "Project"):
        return cls(
            member=member,
            project=project,
            roles=schema.roles,
            join_date=schema.join_date,
        ) """

    def __init__(self, *, member: "Member", project: "Project", roles=None, join_date=None):
        self.member_id = member.id
        self.project_id = project.id
        self.member = member
        self.project = project
        self.roles = roles
        self.join_date = join_date

    @property
    def roles(self) -> List[str]:
        if "," not in self._roles:
            return [] if self._roles == "" else [self._roles]
        return self._roles.split(",")

    @roles.setter
    def roles(self, v: List[str]):
        if v is None:
            self._roles = ""
            return
        if not isinstance(v, list):
            raise ValueError(f'Invalid roles type: "{type(v)}"')
        self._roles = ",".join(v)

    @validates("join_date")
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




