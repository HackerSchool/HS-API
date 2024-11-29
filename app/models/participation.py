from typing import List

from app.extensions import db
from app.services.roles import roles_service

from .utils import _validate_date_string


class ProjectParticipation(db.Model):
    __tablename__ = "projects_participation"

    member_username = db.Column(db.String, db.ForeignKey("users.username"), primary_key=True)
    project_name = db.Column(db.String, db.ForeignKey("projects.name"), primary_key=True)
    entry_date = db.Column(db.String, nullable=False)
    _roles = db.Column("roles", db.String, nullable=False)
    contributions = db.Column(db.String, nullable=True)
    exit_date = db.Column(db.String, nullable=True)

    user = db.relationship("User", back_populates="participations")
    project = db.relationship("Project", back_populates="participations")

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
            if not roles_service.exists_role_in_scope("project", role):
                raise ValueError(f"Role does not exist '{role}'.")

        self._roles = ",".join(roles_list)

    def __init__(
        self,
        entry_date: str,
        roles: List[str],
        contributions: str,
        exit_date: str,
    ):
        self.entry_date = entry_date
        self.roles = roles
        self.contributions = contributions
        self.exit_date = exit_date
        self.check_invariants()

    def check_invariants(self):
        # entry_date
        if not isinstance(self.entry_date, str) or not self.entry_date:
            raise ValueError("Field 'entry_date' must be a non-empty string.")
        _validate_date_string(self.entry_date, "entry_date")

        # contributions
        if not isinstance(self.contributions, str) or len(self.contributions) > 512:
            raise ValueError("Field 'contributions' must be a string with max 512 characters.")

        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("Field 'exit_date' must be a string.")
        if self.exit_date != "":
            _validate_date_string(self.exit_date, "exit_date")

    def to_dict(self):
        return {
            "username": self.member_username,
            "project_name": self.project_name,
            "roles": self.roles,
            "entry_date": self.entry_date,
            "contributions": self.contributions,
            "exit_date": self.exit_date,
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
        return f"<Participation({fields_repr})>"
