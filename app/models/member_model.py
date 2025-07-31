import re
from typing import List, TYPE_CHECKING

import bcrypt
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.extensions import db
from app.utils import is_valid_datestring

if TYPE_CHECKING:
    from app.schemas.member_schema import MemberSchema


def _hash_password(password) -> str:
    # salted encrypted password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


class Member(db.Model):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()

    ist_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    _password: Mapped[str | None] = mapped_column("password", nullable=True)
    _roles: Mapped[str] = mapped_column("roles")
    member_number: Mapped[int] = mapped_column(nullable=True)
    course: Mapped[str] = mapped_column(nullable=True)
    join_date: Mapped[str] = mapped_column(nullable=True)
    exit_date: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    extra: Mapped[str] = mapped_column(nullable=True)

    @classmethod
    def from_schema(self, schema: "MemberSchema"):
        return self(**schema.model_dump())

    def __init__(self, *, ist_id=None, username=None, name=None, email=None, password=None, member_number=None,
                 course=None, roles=None, join_date=None, exit_date=None, description=None, extra=None):
        self.ist_id = ist_id
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.member_number = member_number
        self.course = course
        self.roles = roles
        self.join_date = join_date
        self.exit_date = exit_date
        self.description = description
        self.extra = extra

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, v: str):
        if v is None:
            self._password = None
            return
        if not isinstance(v, str):
            raise ValueError(f'Invalid password type: "{type(v)}"')
        if not 6 <= len(v) <= 256:
            raise ValueError("Invalid password length, minimum 6 and maximum 256 characters")
        self._password = _hash_password(v)

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

    @validates("ist_id")
    def validate_ist_id(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid IST ID type: "{type(v)}"')
        if not re.match(r"^ist1[0-9]{5,7}$", v):
            raise ValueError(f'Invalid IST ID pattern: "{v}"')
        return v

    @validates("username")
    def validate_username(self, k, v):
        if not isinstance(v, str):
            raise ValueError(f'Invalid username type: "{type(v)}"')
        if not isinstance(v, str) or not 3 <= len(v) <= 32:
            raise ValueError(f'Invalid username length, minimum 3 and maximum 32 characters: "{v}"')
        if not re.match(r"^[a-zA-Z0-9]*$", v):
            raise ValueError(f'Invalid characters in username: "{v}"')
        return v

    @validates("name", "email")
    def validate_name(self, k, v):
        if not isinstance(v, str):
            raise ValueError(f'Invalid {k} type: "{type(v)}"')
        if not (1 <= len(v) <= 256):
            raise ValueError(f'Invalid {k} length, minimum 1 and maximum 256 characters: "{v}"')
        return v

    @validates("course")
    def validate_course(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid course type: "{type(v)}"')
        if not (1 <= len(v) <= 8):
            raise ValueError(f'Invalid course length, minimum 1 and maximum 8 characters: "{v}"')
        return v

    @validates("member_number")
    def validate_member_number(self, k, v):
        if v is None:
            return None
        if not isinstance(v, int):
            raise ValueError(f'Invalid member_number type: "{type(v)}"')
        if v < 1:
            raise ValueError(f"Invalid member_number, expected integer greater than 0: Got {v}")
        return v

    @validates("join_date", "exit_date")
    def validate_datestring(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid {k} type: "{type(v)}"')
        if not is_valid_datestring(v):
            raise ValueError(f'Invalid {k} format, expected "YYYY-MM-DD": "{v}"')
        return v

    @validates("description", "extra")
    def validate_description(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid {k} type: "{type(v)}"')
        if len(v) > 2048:
            raise ValueError(f'Invalid {k} length, minimum 0 and maximum 2048 characters: "{v}"')
        return v

    def matches_password(self, password: str):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def __repr__(self):
        return f"<{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})>"
