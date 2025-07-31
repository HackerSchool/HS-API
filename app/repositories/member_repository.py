from app.models.member_model import Member
from app.schemas.update_member_schema import UpdateMemberSchema

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

    def get_member_by_id(self, id: int) -> Member | None:
        return self.db.session.execute(select(Member).where(Member.id == id)).scalars().one_or_none()

    def get_member_by_ist_id(self, ist_id: str) -> Member | None:
        return self.db.session.execute(select(Member).where(Member.ist_id == ist_id)).scalars().one_or_none()

    def get_member_by_username(self, username: str) -> Member | None:
        return self.db.session.execute(select(Member).where(Member.username == username)).scalars().one_or_none()

    def update_member(self, member: Member, update_values: UpdateMemberSchema) -> Member:
        for k, v in update_values.model_dump(exclude_unset=True).items():
            setattr(member, k, v)
        return member

    def delete_member(self, member: Member) -> int:
        self.db.session.execute(delete(Member).where(Member.username == member.username))
        return member.username

