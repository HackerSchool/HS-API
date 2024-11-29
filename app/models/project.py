import re

from app.extensions import db

from .utils import _validate_date_string


class Project(db.Model):
    __tablename__ = "projects"

    name = db.Column(db.String, primary_key=True)
    start_date = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    participations = db.relationship("ProjectParticipation", back_populates="project", cascade="all, delete")

    def __init__(
        self,
        name: str,
        start_date: str,
        state: str,
        description: str,
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
            raise ValueError("Field 'name' must be a non-empty string with max 255 characters.")
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
            raise ValueError("Field 'description' must be a string with max 512 characters")

    def to_dict(self):
        return {
            "name": self.name,
            "start_date": self.start_date,
            "state": self.state,
            "description": self.description,
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
        return f"<Project({fields_repr})>"
