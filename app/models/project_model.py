from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import select, Enum

from app.extensions import db

from app.utils import is_valid_datestring, slugify, ProjectStateEnum

if TYPE_CHECKING:
    from app.schemas.project_schema import ProjectSchema

class Project(db.Model):
    __tablename__ = "projects"

    _name: Mapped[str] = mapped_column("name", primary_key=True)
    slug: Mapped[str] = mapped_column(unique=True)
    state: Mapped[ProjectStateEnum] = mapped_column(Enum(ProjectStateEnum, native_enum=False))
    start_date: Mapped[str] = mapped_column()

    end_date: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)

    @classmethod
    def from_schema(cls, schema: "ProjectSchema"):
        data = schema.model_dump()
        if "slug" in data:
            del data["slug"]
        return cls(**data)

    def __init__(self, *, name=None, state=None, start_date=None, end_date=None, description=None):
        self.name = name
        self.state = state
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = self.validate_name("name", value)
        self.slug = slugify(value)

    @validates("name")
    def validate_name(self, k, v):
        if not isinstance(v, str):
            raise ValueError(f'Invalid name type: "{type(v)}"')
        if isinstance(v, str) and not 2 <= len(v) <= 64:
            raise ValueError(f'Invalid name length, minimum 2 and maximum 64 characters: "{v}"')
        return v

    @validates("slug")
    def validate_slug(self, k, v):
        if db.session.execute(select(Project).where(Project.slug == v)).one_or_none() is not None:
            raise ValueError(f'A slug already exists for this name, please pick a new one: "{v}"')
        return v

    @validates("state")
    def validate_state(self, k, v):
        if not isinstance(v, ProjectStateEnum):
            raise ValueError(f'Invalid state type: "{type(v)}"')
        return v

    @validates("start_date")
    def validate_start_date(self, k, v):
        if not isinstance(v, str):
            raise ValueError(f'Invalid start_date type: "{type(v)}"')
        if not is_valid_datestring(v):
            raise ValueError(f'Invalid start_date format, expected "YYYY-MM-DD": "{v}"')
        return v

    @validates("end_date")
    def validate_end_date(self, k, v):
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError(f'Invalid end_date type: "{type(v)}"')
        if not is_valid_datestring(v):
            raise ValueError(f'Invalid end_date format, expected "YYYY-MM-DD": "{v}"')
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


