# member.py
import bcrypt

from typing import List

from sqlalchemy.orm import joinedload

from app.extensions import db

from app.models import Member

def create_member(
    username: str, 
    password: str, 
    ist_id: str,
    member_number: int, 
    name: str, 
    join_date: str, 
    course: str, 
    email: str, 
    exit_date: str = "",
    description: str = "", 
    extra: str = "",
) -> Member :
    new_member = Member(
        username=username,
        password=password,
        ist_id=ist_id,
        member_number=member_number,
        name=name,
        join_date=join_date,
        course=course,
        email=email,
        exit_date=exit_date,
        description=description,
        extra=extra,
        roles=["member"]
    )
    db.session.add(new_member)
    db.session.commit()
    return new_member

def get_all_members() -> List[Member]:
    """ Returns a list of all members """
    return Member.query.all()

def get_member_by_username(username: str) -> Member | None:
    """ Returns member with given `username` or None if member doesn't exist. """
    return Member.query.filter_by(username=username).first()

def get_member_by_ist_id(ist_id: str) -> Member | None:
    """ Retunrs member with given `ist_id` or None if member doesn't exist """
    return Member.query.filter_by(ist_id=ist_id).first()

def delete_member(member: Member) -> int | None:
    """ Deletes given `member` from the DB and returns member's username. """
    db.session.delete(member)
    db.session.commit()
    return member.username

def edit_member(member: Member, **kwargs) -> Member:
    """ 
    Edit given `member` with provided information. 
    Returns updated member.
    """
   # updating the fields 
    for field, val in kwargs.items():
        setattr(member, field, val)
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member
    
def edit_member_password(member: Member, password: str) -> Member:
    """ 
    Updates given user password.
    Returns member.
    """
    member.password = password
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member

def add_member_role(member: Member, role: str) -> List[str] | None:
    """ 
    Adds given `role` to member roles and returns the updated roles list. 
    If the member already has the given role returns None.
    """
    roles = member.roles
    if role in roles:
        return None

    roles += [role,]
    member.roles = roles
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member.roles
 
def remove_member_role(member: Member, role: str) -> List[str] | None:
    """ 
    Remove `role` from member and returns the updated roles list.
    If the member does not have the given role returns None.
    """
    roles = member.roles
    if role not in role:
        return None

    roles.remove(role)
    member.roles = roles
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member.roles
    
def create_applicant(
    username: str, 
    password: str, 
    ist_id: str,
    member_number: int, 
    name: str, 
    join_date: str, 
    course: str, 
    email: str, 
    exit_date: str = "",
    description: str = "", 
    extra: str = "",
) -> Member :
    new_member = Member(
        username=username,
        password=password,
        ist_id=ist_id,
        member_number=member_number,
        name=name,
        join_date=join_date,
        course=course,
        email=email,
        exit_date=exit_date,
        description=description,
        extra=extra,
        roles=["applicant"]
    )
    db.session.add(new_member)
    db.session.commit()
    return new_member
