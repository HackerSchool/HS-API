# member.py
import bcrypt

from typing import List

from sqlalchemy.orm import joinedload

from app.extensions import db

from app.models import Member

def _hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_member(
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
) -> Member :
    hashed_password = _hash_password(password)
    new_member = Member(
        ist_id=ist_id,
        member_number=member_number,
        name=name,
        username=username,
        password=hashed_password,
        join_date=join_date,
        course=course,
        description=description,
        exit_date=exit_date,
        email=email,
        extra=extra,
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
    member.password = _hash_password(password)
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member

def add_member_tag(member: Member, tag: str) -> List[str] | None:
    """ 
    Adds given `tag` to member tags and returns the updated tags list. 
    If the member already has the tag returns None.
    """
    tags = member.tags
    if tag in tags:
        return None

    tags += [tag,]
    member.tags = tags
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member.tags
 
def remove_member_tag(member: Member, tag: str) -> List[str] | None:
    """ 
    Remove `tag` from member and returns the updated tags list.
    If the member does not have the tag returns None.
    """
 
    tags = member.tags
    if tag not in tags:
        return None

    tags.remove(tag)
    member.tags = tags
    member.check_invariants() # this will fail if the fields are invalid

    db.session.commit()
    return member.tags 
    
