import re
from typing import List

from app.extensions import db
from app.services.roles import roles_service

from .utils import _hash_password, _validate_date_string


class User(db.Model):
    __tablename__ = "users"

    ist_id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    course = db.Column(db.String, nullable=False)
    member_number = db.Column(db.Integer)
    join_date = db.Column(db.String)
    exit_date = db.Column(db.String)
    description = db.Column(db.String)
    extra = db.Column(db.String)
    _roles = db.Column("roles", db.String)

    participations = db.relationship("ProjectParticipation", back_populates="user", cascade="all, delete")

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
        if not isinstance(roles_list, list) or len(roles_list) == 0:
            raise ValueError("Field 'roles' must be a non-empty list.")

        for role in roles_list:
            if role == "":
                raise ValueError("A role must be a non-empty string.")
            if not roles_service.exists_role_in_scope("general", role):
                raise ValueError(f"Role does not exist '{role}'.")

        self._roles = ",".join(roles_list)

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str):
        # password
        if not isinstance(password, str) or not password or len(password) > 255:
            raise ValueError("Field 'password' must be a non-empty string with max 255 characters.")
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
            raise ValueError("Invalid username, length must be between 2 to 20 characters.")
        if not re.match(r"^[a-zA-Z0-9]+$", self.username):
            raise ValueError("Invalid username, only allowed characters in the ranges a-z A-Z and 0-9.")

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
            raise ValueError("Field 'name' must be a non-empty string with max 255 characters.")

        # email
        if not isinstance(self.email, str) or not self.email or len(self.email) > 255:
            raise ValueError("Field 'email' must be a non-empty string with max 255 characters.")

        # course
        if not isinstance(self.course, str) or not self.course or len(self.course) > 8:
            raise ValueError("Field 'course' must be a non-empty string with max 8 characters.")

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
            raise ValueError("Field 'description' must be a string with max 512 characters.")

        # extra
        if not isinstance(self.extra, str) or len(self.extra) > 512:
            raise ValueError("Field 'extra' must be a string with max 512 characters.")

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

    def __repr__(self):
        attr_fields = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("_")  # Exclude private/internal attributes
        }
        property_fields = {
            key: getattr(self, key) for key in dir(self) if isinstance(getattr(self.__class__, key, None), property)
        }
        all_fields = {**attr_fields, **property_fields}
        fields_repr = ", ".join(f"{key}={value!r}" for key, value in all_fields.items())
        return f"<User({fields_repr})>"
