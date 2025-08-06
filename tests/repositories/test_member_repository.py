import pytest

from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db

from app.repositories.member_repository import MemberRepository
from app.models.member_model import Member
from app.schemas.update_member_schema import UpdateMemberSchema

base_member = {
    "ist_id": "ist100000",
    "username": "username",
    "name": "name",
    "email": "email",
}

@pytest.fixture(scope="function")
def app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    app = create_app()
    with app.app_context():
        db.create_all()
        yield
        db.session.commit() # flush transactions or it won't be able to drop
        db.drop_all()

@pytest.fixture
def member_repository():
    return MemberRepository(db=db)

def test_create_member(app, member_repository: MemberRepository):
    new_member = Member(**base_member)
    member_repository.create_member(new_member)
    created_member = db.session.execute(select(Member).where(Member.ist_id == new_member.ist_id)).scalars().one_or_none()
    assert created_member is not None
    assert new_member.ist_id == created_member.ist_id
    assert new_member.username == created_member.username
    assert new_member.name == created_member.name
    assert new_member.email == created_member.email

def test_get_member_by_id(app, member_repository: MemberRepository):
    member = Member(**base_member)
    member.id = 1
    db.session.add(member)
    gotten_member = member_repository.get_member_by_id(member.id)
    assert gotten_member is not None
    assert member.ist_id == gotten_member.ist_id
    assert member.username == gotten_member.username
    assert member.name == gotten_member.name
    assert member.email == gotten_member.email

def test_get_member_by_ist_id(app, member_repository: MemberRepository):
    member = Member(**base_member)
    db.session.add(member)
    gotten_member = member_repository.get_member_by_ist_id(member.ist_id)
    assert gotten_member is not None
    assert member.ist_id == gotten_member.ist_id
    assert member.username == gotten_member.username
    assert member.name == gotten_member.name
    assert member.email == gotten_member.email

def test_get_member_by_username(app, member_repository: MemberRepository):
    member = Member(**base_member)
    db.session.add(member)
    gotten_member = member_repository.get_member_by_username(member.username)

    assert member.ist_id == gotten_member.ist_id
    assert member.username == gotten_member.username
    assert member.name == gotten_member.name
    assert member.email == gotten_member.email

def test_get_no_member_by_username(app, member_repository: MemberRepository):
    assert member_repository.get_member_by_username(base_member["username"]) is None

def test_get_no_member_by_ist_id(app, member_repository: MemberRepository):
    assert member_repository.get_member_by_ist_id(base_member["ist_id"]) is None

def test_delete_member(app, member_repository: MemberRepository):
    member = Member(**base_member)
    db.session.add(member)

    username = member_repository.delete_member(member)
    assert username == member.username
    assert db.session.execute(select(Member).where(Member.username == member.username)).scalars().one_or_none() is None

def test_get_members(app, member_repository: MemberRepository):
    members: set = set()
    for i in range(3):
        data = {**base_member}
        data["ist_id"] = data["ist_id"] + str(i)
        data["username"] = data["username"] + str(i)
        data["email"] = data["email"] + str(i)
        member = Member(**data)
        db.session.add(member)
        members.add(member)

    gotten_members = member_repository.get_members()
    assert {m.ist_id for m in members} == {gm.ist_id for gm in gotten_members}

def test_update_member(app, member_repository: MemberRepository):
    member = Member(**base_member)
    db.session.add(member)
    new_data = {
        "ist_id": "ist100001",
        "username": "username2",
        "name": "name2",
        "email": "email2"
    }
    update_values = UpdateMemberSchema(**new_data)
    updated_member = member_repository.update_member(member, update_values)

    gotten_member = db.session.execute(select(Member).where(Member.ist_id == member.ist_id)).scalars().one_or_none()
    assert gotten_member.username == updated_member.username
    assert gotten_member.name == updated_member.name
    assert gotten_member.email == updated_member.email

