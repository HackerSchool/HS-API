from datetime import date
import re

from app.extensions import db
from app.extensions import tags_handler

def _validate_date_string(date_string: str, field_name: str):
    """Validate and convert date string to datetime.date."""
    try:
        date.fromisoformat(date_string)
    except ValueError:
        raise ValueError(f"'{field_name}' must be a valid date in the format YYYY-MM-DD.")


class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ist_id = db.Column(db.String, nullable=False)
    member_number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    join_date = db.Column(db.String, nullable=False)
    course = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    exit_date = db.Column(db.String)
    description = db.Column(db.String)
    extra = db.Column(db.String)
    tags = db.Column(db.String)
    
    projects = db.relationship('MemberProjects', back_populates="member", lazy="joined")
    
    def __init__(
        self,
        ist_id: str,
        member_number: int,
        name: str,
        username: str,
        password: str,
        join_date: str,
        course: str,
        email: str,
        exit_date: str = "",
        description: str = "",
        extra: str = "",
        tags: str = "member",
    ):
        self.ist_id = ist_id
        self.member_number = member_number
        self.name = name
        self.username = username
        self.password = password
        self.join_date = join_date
        self.exit_date = exit_date
        self.course = course
        self.description = description 
        self.email = email
        self.extra = extra
        self.tags = tags
        self.check_invariants()

    def check_invariants(self):
        # ist_id
        if not isinstance(self.ist_id, str) or not self.ist_id:
            raise ValueError("ist_id must be a non-empty string.")

        # member_number
        if not isinstance(self.member_number, int) or self.member_number <= 0:
            raise ValueError("member_number must be a positive integer.")

        # name
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be a non-empty string.")

        # username
        if not isinstance(self.username, str) or not self.username:
            raise ValueError("'username' must be a non-empty string.")
        if len(self.username) > 20 or len(self.username) < 2:
            raise ValueError("Invalid username, length must be between 2 to 20 characters")
        if not re.match(r"^[a-zA-Z0-9]+$", self.username):
            raise ValueError("Invalid username, only allowed characters in the ranges a-z A-Z and 0-9")

        # password
        if not isinstance(self.password, str) or not self.password:
            raise ValueError("'password' must be a non-empty string.")

        # email
        if not isinstance(self.email, str) or not self.email:
            raise ValueError("'email' must be a non-empty string.")

        # course
        if not isinstance(self.course, str) or not self.course:
            raise ValueError("'course' must be a non-empty string.")

        # description
        if not isinstance(self.description, str):
            raise ValueError("'description' must be a string.")

        # extra
        if not isinstance(self.extra, str):
            raise ValueError("'extra' must be a string.")
        
        # tags
        if not isinstance(self.tags, str) or self.tags == "":
            raise ValueError("Member must have at least 1 tag")
        tags = self.tags.split(",") if "," in self.tags else [self.tags,]
        for tag in tags:
            if tag not in tags_handler.tags.keys():
                raise ValueError(f"Unknown tag '{tag}'")

        # join_date
        if not isinstance(self.join_date, str) or not self.join_date:
            raise ValueError("'join_date' must be a non-empty string.")
        _validate_date_string(self.join_date, "join_date")

        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("'exit_date' must be a string.")
        if self.exit_date != "":
            _validate_date_string(self.exit_date, "exit_date")

    def to_dict(self):
        return {
            "id": self.id,
            "ist_id": self.ist_id,
            "member_number": self.member_number,
            "name": self.name,
            "username": self.username,
            "join_date": self.join_date,
            "exit_date": self.exit_date,
            "course": self.course,
            "description": self.description,
            "email": self.email,
            "extra": self.extra,
            "tags": self.tags,
        }
    

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    members = db.relationship('MemberProjects', back_populates='project')

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
        self.name = self.name.replace(" ", "-") # remove whitespaces for prettier URLs 

    def check_invariants(self):
        # name
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("name must be a non-empty string.")
        if len(self.name) > 255:
            raise ValueError("Invalid name, please keep it shorter...")
        if not re.match(r"^[a-zA-Z0-9-_~]+$", self.name):
            raise ValueError("Invalid username, only allowed characters in the ranges a-z A-Z and 0-9 and ' ' '-' '_' '~'")

        # state
        if not isinstance(self.state, str) or not self.state:
            raise ValueError("'username' must be a non-empty string.")

        if not isinstance(self.start_date, str) or not self.start_date:
            raise ValueError("'start_date' must be a non-empty string.")
        # start_date
        _validate_date_string(self.start_date, "start")

        # description
        if not isinstance(self.description, str):
            raise ValueError("'description' must be a string.")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date,
            "state": self.state,
            "description": self.description,
        }


class MemberProjects(db.Model):
    __tablename__ = 'member_projects'

    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    entry_date = db.Column(db.String, nullable=False)
    contributions = db.Column(db.String, nullable=True)
    exit_date = db.Column(db.String, nullable=True)

    member = db.relationship('Member', back_populates="projects", cascade='all, delete')
    project = db.relationship('Project', back_populates="members" , cascade='all, delete')

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
            raise ValueError("'entry_date' must be a non-empty string.")
        _validate_date_string(self.entry_date, "entry_date")

        # contributinos
        if not isinstance(self.contributions, str):
            raise ValueError("'contributions' must be a string.")
            
        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("'exit_date' must be a string.")
        if self.exit_date != "":
            _validate_date_string(self.exit_date, "exit_date")

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "project_id": self.project_id,
            "entry_date": self.entry_date,
            "contributions": self.contributions,
            "exit_date": self.exit_date
        }
