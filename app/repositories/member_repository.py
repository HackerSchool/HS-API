from app.models.member_model import Member

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete, update

from typing import List


class MemberRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_member(self, member: Member) -> Member:
        self.db.session.add(member)
        return member

    def get_members(self) -> List[Member]:
        return self.db.session.execute(select(Member)).scalars().fetchall()

    def get_member_by_ist_id(self, ist_id: str) -> Member | None:
        return self.db.session.execute(select(Member).where(Member.ist_id == ist_id)).scalars().one_or_none()

    def get_member_by_username(self, username: str) -> Member | None:
        return self.db.session.execute(select(Member).where(Member.username == username)).scalars().one_or_none()

    def update_member_by_ist_id(self, ist_id: str, **values) -> None:
        self.db.session.execute(update(Member).where(Member.ist_id == ist_id).values(**values))

    def delete_member_by_ist_id(self, ist_id: str) -> None:
        self.db.session.execute(delete(Member).where(Member.ist_id == ist_id))

    def delete_member_by_username(self, username: str) -> None:
        self.db.session.execute(delete(Member).where(Member.username == username))
