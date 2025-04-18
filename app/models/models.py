from typing import List

import re
import bcrypt

from datetime import date

from app.extensions import db
from app.extensions import roles_handler


def _hash_password(password) -> str:
    # Generate a salt and hash the password
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def _validate_date_string(date_string: str, field_name: str):
    """Validate and convert date string to datetime.date."""
    try:
        date.fromisoformat(date_string)
    except ValueError:
        raise ValueError(
            f"'{field_name}' must be a valid date in the format YYYY-MM-DD."
        )


class Member(db.Model):
    __tablename__ = "members"

    username = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)
    ist_id = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    course = db.Column(db.String, nullable=False)
    member_number = db.Column(db.Integer)
    join_date = db.Column(db.String)
    exit_date = db.Column(db.String)
    description = db.Column(db.String)
    extra = db.Column(db.String)
    _roles = db.Column("roles", db.String)

    projects = db.relationship("MemberProjects", back_populates="member")

    @property
    def roles(self) -> List[str]:
        return (
            [
                self._roles,
            ]
            if "," not in self._roles
            else self._roles.split(",")
        )

    @roles.setter
    def roles(self, roles_list: List[str]):
        self._roles = ",".join(roles_list)

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str):
        # password
        if not isinstance(password, str) or not password or len(password) > 255:
            raise ValueError(
                "Field 'password' must be a non-empty string with max 255 characters."
            )
        self._password = _hash_password(password)

    def __init__(
        self,
        username: str,
        password: str,
        ist_id: str,
        name: str,
        email: str,
        course: str,
        member_number: int,
        join_date: str,
        exit_date: str,
        description: str,
        extra: str,
        roles: List[str],
    ):
        self.username = username
        self.password = password
        self.ist_id = ist_id
        self.name = name
        self.email = email
        self.course = course
        self.member_number = member_number
        self.join_date = join_date
        self.exit_date = exit_date
        self.description = description
        self.extra = extra
        self.roles = roles
        self.check_invariants()

    def check_invariants(self):
        # username
        if not isinstance(self.username, str) or not self.username:
            raise ValueError("Field 'username' must be a non-empty string.")
        if len(self.username) > 20 or len(self.username) < 2:
            raise ValueError(
                "Invalid username, length must be between 2 to 20 characters"
            )
        if not re.match(r"^[a-zA-Z0-9]+$", self.username):
            raise ValueError(
                "Invalid username, only allowed characters in the ranges a-z A-Z and 0-9"
            )

        # ist_id
        if (
            not isinstance(self.ist_id, str)
            or not self.ist_id
            or len(self.ist_id) < 4
            or len(self.ist_id) > 20
            or not self.ist_id.startswith("ist1")
        ):
            raise ValueError("Field 'ist_id' must be a valid IST student number.")

        # name
        if not isinstance(self.name, str) or not self.name or len(self.name) > 255:
            raise ValueError(
                "Field 'name' must be a non-empty string with max 255 characters."
            )

        # email
        if not isinstance(self.email, str) or not self.email or len(self.email) > 255:
            raise ValueError(
                "Field 'email' must be a non-empty string with max 255 characters."
            )

        # course
        if not isinstance(self.course, str) or not self.course or len(self.course) > 10:
            raise ValueError(
                "Field 'course' must be a non-empty string with max 8 characters."
            )

        # member_number
        if not isinstance(self.member_number, int) or self.member_number < 0:
            raise ValueError("Field 'member_number' must be a positive integer.")

        # join_date
        if not isinstance(self.join_date, str):
            raise ValueError("Field 'join_date' must be a string.")
        if self.join_date != "":
            _validate_date_string(self.join_date, "join_date")

        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("Field 'exit_date' must be a string.")
        if self.exit_date != "":
            _validate_date_string(self.exit_date, "exit_date")

        # description
        if not isinstance(self.description, str) or len(self.description) > 512:
            raise ValueError(
                "Field 'description' must be a string with max 512 characters."
            )

        # extra
        if not isinstance(self.extra, str) or len(self.exit_date) > 512:
            raise ValueError("Field 'extra' must be a string with max 512 characters.")

        # roles
        if not isinstance(self.roles, list) or (
            len(self.roles) == 1 and self.roles[0] == ""
        ):
            raise ValueError("Field 'roles' must have at least 1 role")
        for role in self.roles:
            if not roles_handler.exists_role(role):
                raise ValueError(f"Unknown role '{role}'")

    def to_dict(self):
        return {
            "username": self.username,
            "ist_id": self.ist_id,
            "name": self.name,
            "course": self.course,
            "email": self.email,
            "member_number": self.member_number,
            "join_date": self.join_date,
            "exit_date": self.exit_date,
            "description": self.description,
            "extra": self.extra,
            "roles": self.roles,
        }


class Project(db.Model):
    __tablename__ = "projects"

    name = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    members = db.relationship("MemberProjects", back_populates="project")

    def __init__(
        self,
        name: str,
        start_date: str,
        state: str,
        description: str = "",
    ):
        self.name = name
        self.start_date = start_date
        self.state = state
        self.description = description

        self.post_init()
        self.check_invariants()

    def post_init(self):
        self.name = self.name.replace(" ", "-")  # remove whitespaces for prettier URLs

    def check_invariants(self):
        # name
        if not isinstance(self.name, str) or not self.name or len(self.name) > 255:
            raise ValueError(
                "Field 'name' must be a non-empty string with max 255 characters."
            )
        if not re.match(r"^[a-zA-Z0-9-_~]+$", self.name):
            raise ValueError(
                "Invalid username, only allowed characters in the ranges a-z A-Z and 0-9 and ' ' '-' '_' '~'"
            )

        # state
        if not isinstance(self.state, str) or not self.state:  # TODO add states enum
            raise ValueError("Field 'state' must be a non-empty string.")

        if not isinstance(self.start_date, str) or not self.start_date:
            raise ValueError("Field 'start_date' must be a non-empty string.")
        # start_date
        _validate_date_string(self.start_date, "start")

        # description
        if not isinstance(self.description, str) or len(self.description) > 512:
            raise ValueError(
                "Field 'description' must be a string with max 512 characters"
            )

    def to_dict(self):
        return {
            "name": self.name,
            "start_date": self.start_date,
            "state": self.state,
            "description": self.description,
        }


class MemberProjects(db.Model):
    __tablename__ = "member_projects"

    member_username = db.Column(
        db.String, db.ForeignKey("members.username"), primary_key=True
    )
    project_name = db.Column(
        db.String, db.ForeignKey("projects.name"), primary_key=True
    )
    entry_date = db.Column(db.String, nullable=False)
    contributions = db.Column(db.String, nullable=True)
    exit_date = db.Column(db.String, nullable=True)

    member = db.relationship("Member", back_populates="projects", cascade="all, delete")
    project = db.relationship(
        "Project", back_populates="members", cascade="all, delete"
    )

    def __init__(
        self,
        entry_date: str,
        contributions: str = "",
        exit_date: str = "",
    ):
        self.entry_date = entry_date
        self.contributions = contributions
        self.exit_date = exit_date
        self.check_invariants()

    def check_invariants(self):
        # entry_date
        if not isinstance(self.entry_date, str) or not self.entry_date:
            raise ValueError("Field 'entry_date' must be a non-empty string.")
        _validate_date_string(self.entry_date, "entry_date")

        # contributinos
        if not isinstance(self.contributions, str) or len(self.contributions) > 512:
            raise ValueError(
                "Field 'contributions' must be a string with max 512 characters."
            )

        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("Field 'exit_date' must be a string.")
        if self.exit_date != "":
            _validate_date_string(self.exit_date, "exit_date")

    def to_dict(self):
        return {
            "username": self.member_username,
            "project_name": self.project_name,
            "entry_date": self.entry_date,
            "contributions": self.contributions,
            "exit_date": self.exit_date,
        }
