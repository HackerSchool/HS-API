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
) -> dict :
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
        tags="member",
    )
    db.session.add(new_member)
    db.session.commit()
    return new_member


def get_all_members() -> List[Member]:
    return [member for member in Member.query.all()]

def get_member_by_username(username: str) -> Member | None:
    return Member.query.filter_by(username=username).first()

def delete_member(member: Member) -> int | None:
    db.session.delete(member)
    db.session.commit()
    return member.id

def edit_member(member: Member, **kwargs) -> Member:
   # updating the fields 
    for field, val in kwargs.items():
        setattr(member, field, val)
    member.check_invariants() # this will fail if the fields are invalid
    db.session.commit()
    return member
    
def edit_member_password(member: Member, password: str) -> Member:
    member.password = _hash_password(password)
    member.check_invariants() # this will fail if the fields are invalid
    db.session.commit()
    return member

def get_member_tags(member: Member) -> List[str]:
    return [member.tags,] if "," not in member.tags else member.tags.split(",") 

def add_member_tag(member: Member, tag: str) -> List[str]:
    # already has tag
    if tag in member.tags:
        return [member.tags,] if "," not in member.tags else member.tags.split(",") 
    member.tags += f",{tag}"
    member.check_invariants() # this will fail if the fields are invalid
    db.session.commit()
    return [member.tags,] if "," not in member.tags else member.tags.split(",") 
 
def remove_member_tag(member: Member, target_tag: str) -> List[str]:
    tags = member.tags.split(",") if len(member.tags) > 1 else [member.tags,]
    if target_tag not in tags:
        return None

    tags = ",".join(list(filter(lambda x: x != target_tag, tags))) # remove tag and recreate tags string

    member.tags = tags
    member.check_invariants()
    db.session.commit()
    return member.tags if "," not in member.tags else member.tags.split(",") 
    
