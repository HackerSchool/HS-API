import re
from typing import List, TYPE_CHECKING

import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship

from app.extensions import db
from app.utils import is_valid_datestring

if TYPE_CHECKING:
    from app.schemas.point_schema import PointSchema
    from .member_model import Member 

class Point(db.Model):
    __tablename__ = "points"

    id: Mapped[int] = mapped_column(primary_key=True)
    pj: Mapped[int] = mapped_column(nullable=True)
    pcc: Mapped[int] = mapped_column(nullable=True)
    ps: Mapped[int] = mapped_column(nullable=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), unique=True)
    member: Mapped["Member"] = relationship("Member", back_populates="points")


    @classmethod
    def from_schema(cls, schema: "PointSchema", member: Member):
    return cls(
        member=member,
        pj=schema.pj,
        pcc=schema.pcc,
        ps=schema.ps
    )

    def __init__(self, *, member: "Member", pj=None, pcc=None, ps=None):
        self.member = member
        self.pj = pj
        self.pcc = pcc
        self.ps = ps

    def __repr__(self):
        return f"<{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})>"




