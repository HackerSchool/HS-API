# member.py
from typing import List

from app.extensions import db
from app.models import User


def get_all_users() -> List[User]:
    """Returns a list of all users."""
    return User.query.all()


def get_user_by_username(username: str) -> User | None:
    """Returns user with given `username` or None if user doesn't exist."""
    return User.query.filter_by(username=username).one_or_none()


def get_user_by_ist_id(ist_id: str) -> User | None:
    """Retunrs member with given `ist_id` or None if user doesn't exist."""
    return User.query.filter_by(ist_id=ist_id).one_or_none()


def delete_user(user: User) -> int | None:
    """Deletes given `user` from the DB and returns user's username."""
    db.session.delete(user)
    db.session.commit()
    return user.username


def edit_user(user: User, **kwargs) -> User:
    """
    Edit given `user` with provided information.
    Returns updated user.
    """
    # updating the fields
    for field, val in kwargs.items():
        setattr(user, field, val)
    user.check_invariants()  # this will fail if the fields are invalid
    db.session.commit()
    return user


def edit_user_password(user: User, password: str) -> User:
    """
    Updates given `user` password.
    Returns updated user.
    """
    user.password = password
    user.check_invariants()  # this will fail if the fields are invalid

    db.session.commit()
    return user


def add_user_role(user: User, role: str) -> List[str] | None:
    """
    Adds `role` to given `user` and returns the updated roles list.
    If the user already has the given role returns None.
    """
    roles = user.roles
    if role in roles:
        return None

    roles += [
        role,
    ]
    user.roles = roles
    user.check_invariants()  # this will fail if the fields are invalid

    db.session.commit()
    return user.roles


def remove_user_role(user: User, role: str) -> List[str] | None:
    """
    Removes `role` from given `user` and returns the updated roles list.
    If the user does not have the given role returns None.
    """
    roles = user.roles
    if role not in role:
        return None

    roles.remove(role)
    user.roles = roles
    user.check_invariants()  # this will fail if the fields are invalid

    db.session.commit()
    return user.roles


def create_member(
    username: str,
    password: str,
    ist_id: str,
    name: str,
    email: str,
    course: str,
    member_number: int,
    join_date: str,
    exit_date: str = "",
    description: str = "",
    extra: str = "",
) -> User:
    """Creates a new member and returns created User."""
    new_member = User(
        username=username,
        password=password,
        ist_id=ist_id,
        name=name,
        email=email,
        course=course,
        member_number=member_number,
        join_date=join_date,
        exit_date=exit_date,
        description=description,
        extra=extra,
        roles=["member"],
    )
    db.session.add(new_member)
    db.session.commit()
    return new_member


def create_applicant(
    username: str,
    password: str,
    ist_id: str,
    name: str,
    email: str,
    course: str,
) -> User:
    """Creates a new applicant with member number 0 and returns created User."""
    new_applicant = User(
        username=username,
        password=password,
        ist_id=ist_id,
        name=name,
        email=email,
        course=course,
        member_number=0,
        join_date="",
        exit_date="",
        description="",
        extra="",
        roles=["applicant"],
    )
    db.session.add(new_applicant)
    db.session.commit()
    return new_applicant
