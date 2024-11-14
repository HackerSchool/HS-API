from typing import List

import re
import bcrypt

from datetime import date

from app.extensions import db
from app.extensions import roles_handler

def _hash_password(password) -> str:
    # Generate a salt and hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def _validate_date_string(date_string: str, field_name: str):
    """Validate and convert date string to datetime.date."""
    try:
        date.fromisoformat(date_string)
    except ValueError:
        raise ValueError(f"'{field_name}' must be a valid date in the format YYYY-MM-DD.")


class Member(db.Model):
    __tablename__ = 'members'
    
    username = db.Column(db.String, primary_key=True, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)
    ist_id = db.Column(db.String, nullable=False, unique=True)
    member_number = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    join_date = db.Column(db.String, nullable=False)
    course = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    exit_date = db.Column(db.String)
    description = db.Column(db.String)
    extra = db.Column(db.String)
    _roles = db.Column("roles", db.String)
    
    projects = db.relationship('MemberProjects', back_populates="member")
    
    @property
    def roles(self) -> List[str]:
        return [self._roles,] if "," not in self._roles else self._roles.split(",")
    
    @roles.setter
    def roles(self, roles_list: List[str]):
        self._roles = ",".join(roles_list)
    
    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, password: str):
        self._password = _hash_password(password)

    def __init__(
        self,
        username: str,
        password: str,
        ist_id: str,
        member_number: int,
        name: str,
        join_date: str,
        course: str,
        email: str,
        exit_date: str,
        description: str,
        extra: str,
        roles: List[str],
    ):
        self.username = username
        self.password = password
        self.ist_id = ist_id
        self.member_number = member_number
        self.name = name
        self.join_date = join_date
        self.exit_date = exit_date
        self.course = course
        self.description = description 
        self.email = email
        self.extra = extra
        self.roles = roles 
        self.check_invariants()

    def check_invariants(self):
        # username
        if not isinstance(self.username, str) or not self.username:
            raise ValueError("Field 'username' must be a non-empty string.")
        if len(self.username) > 20 or len(self.username) < 2:
            raise ValueError("Invalid username, length must be between 2 to 20 characters")
        if not re.match(r"^[a-zA-Z0-9]+$", self.username):
            raise ValueError("Invalid username, only allowed characters in the ranges a-z A-Z and 0-9")

        # password
        if not isinstance(self.password, str) or not self.password:
            raise ValueError("Field 'password' must be a non-empty string.")

        # ist_id
        if not isinstance(self.ist_id, str) or not self.ist_id:
            raise ValueError("Field 'ist_id' must be a non-empty string.")

        # member_number
        if not isinstance(self.member_number, int) or self.member_number < 0:
            raise ValueError("Field 'member_number' must be a positive integer.")

        # name
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Field 'name' must be a non-empty string.")

        # email
        if not isinstance(self.email, str) or not self.email:
            raise ValueError("Field 'email' must be a non-empty string.")

        # course
        if not isinstance(self.course, str) or not self.course:
            raise ValueError("Field 'course' must be a non-empty string.")

        # description
        if not isinstance(self.description, str):
            raise ValueError("Field 'description' must be a string.")

        # extra
        if not isinstance(self.extra, str):
            raise ValueError("Field 'extra' must be a string.")
        
        # roles 
        if not isinstance(self.roles, list) or len(self.roles) == 0:
            raise ValueError("Field 'roles' must have at least 1 role")
        for role in self.roles:
            if role not in roles_handler.roles.keys():
                raise ValueError(f"Unknown role '{role}'")

        # join_date
        if not isinstance(self.join_date, str) or not self.join_date:
            raise ValueError("Field 'join_date' must be a non-empty string.")
        _validate_date_string(self.join_date, "join_date")

        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("Field 'exit_date' must be a string.")
        if self.exit_date != "":
            _validate_date_string(self.exit_date, "exit_date")

    def to_dict(self):
        return {
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
            "roles": self.roles,
        }
    

class Project(db.Model):
    __tablename__ = 'projects'

    name = db.Column(db.String, primary_key=True, unique=True, nullable=False)
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
            "name": self.name,
            "start_date": self.start_date,
            "state": self.state,
            "description": self.description,
        }


class MemberProjects(db.Model):
    __tablename__ = 'member_projects'

    member_username = db.Column(db.String, db.ForeignKey('members.username'), primary_key=True)
    project_name = db.Column(db.String, db.ForeignKey('projects.name'), primary_key=True)
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
            raise ValueError("Field 'entry_date' must be a non-empty string.")
        _validate_date_string(self.entry_date, "entry_date")

        # contributinos
        if not isinstance(self.contributions, str):
            raise ValueError("Field 'contributions' must be a string.")
            
        # exit_date
        if not isinstance(self.exit_date, str):
            raise ValueError("Field 'exit_date' must be a string.")
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
