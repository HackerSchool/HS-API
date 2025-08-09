import pytest

from unittest.mock import MagicMock
from flask.testing import FlaskClient
from http import HTTPStatus

from app import create_app
from app.models.member_model import Member
from app.schemas.member_schema import MemberSchema
from app.repositories.member_repository import MemberRepository

base_member = {
    "ist_id": "ist100000",
    "username": "username",
    "name": "name",
    "email": "email",
}

@pytest.fixture
def mock_member_repo():
    return MagicMock()

@pytest.fixture
def client(mock_member_repo):
    from app.config import Config
    Config.ENABLED_ACCESS_CONTROL = False

    app = create_app(member_repo=mock_member_repo)
    with app.test_client() as client:
        yield client

def test_get_member(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_username.return_value = Member(**base_member)
    rsp = client.get(f"/members/{base_member['username']}")

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in base_member.items():
        assert rsp.json[k] == v

def test_get_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_username.return_value = None
    rsp = client.get(f"/members/{base_member['username']}")

    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_create_member(client: FlaskClient, mock_member_repo: MemberRepository):
    member = Member(**base_member)
    schema = MemberSchema.from_member(member)
    mock_member_repo.create_member.return_value = member
    mock_member_repo.get_member_by_ist_id.return_value = None
    mock_member_repo.get_member_by_username.return_value = None

    rsp = client.post(f"/members", json=schema.model_dump())
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in base_member.items():
        assert rsp.json[k] == v

def test_create_member_duplicate_ist_id(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_ist_id.return_value = not None  # simply not None
    schema = MemberSchema(**base_member)
    rsp = client.post(f"/members", json=schema.model_dump())
    assert rsp.status_code == HTTPStatus.CONFLICT

def test_create_member_duplicate_username(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_ist_id.return_value = None
    mock_member_repo.get_member_by_username.return_value = True  # simply a not None value
    schema = MemberSchema(**base_member)
    rsp = client.post(f"/members", json=schema.model_dump())
    assert rsp.status_code == HTTPStatus.CONFLICT

def test_get_members(client: FlaskClient, mock_member_repo: MemberRepository):
    # Quick explanation: Use sets to determine that the response matches the mock,
    #   because sets don't care for order, unlike lists or tuples.
    # Needs frozenset because dicts aren't hashable and can't be put into sets.
    members: list = []
    expected_members: set = set()
    for i in range(3):
        username = base_member["username"] + str(i)
        ist_id = base_member["ist_id"] + str(i)

        m = Member(**base_member)
        m.username = username
        m.ist_id = ist_id
        members.append(m)

        expected = {**base_member, "username": username, "ist_id": ist_id}
        expected_members.add(frozenset(expected.items()))

    mock_member_repo.get_members.return_value = members
    rsp = client.get("/members")

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert isinstance(rsp.json, list)
    assert len(rsp.json) == 3
    # remove all keys not found in base_user from each json object
    ret_members: set = set()
    for i in range(3):
        filtered_obj = {k: v for k, v in rsp.json[i].items() if k in base_member.keys()}
        ret_members.add(frozenset(filtered_obj.items()))

    assert ret_members == expected_members

def test_get_members_empty(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_members.return_value = []
    rsp = client.get("/members")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json == []

def test_update_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_username.return_value = None
    rsp = client.put(f"/members/{base_member['ist_id']}")
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_update_member_conflict(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_username.return_value = not None
    rsp = client.put(f"/members/{base_member['username']}", json={"username": "newusername"})
    assert rsp.status_code == HTTPStatus.CONFLICT.value
    assert rsp.mimetype == "application/json"

def test_update_member(client: FlaskClient, mock_member_repo: MemberRepository):
    update_member = {**base_member, "email": "new-email"}
    mock_member_repo.get_member_by_username.return_value = not None
    mock_member_repo.side_effects = [not None, None]
    mock_member_repo.update_member.return_value = Member(**update_member)
    rsp = client.put(f"/members/{base_member['ist_id']}", json={"email": "new-email"})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in update_member.items():
        assert rsp.json[k] == v

def test_delete_member_not_found(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_username.return_value = None
    rsp = client.delete(f"/members/{base_member['username']}")
    assert rsp.status_code == 404
    assert rsp.mimetype == "application/json"

def test_delete_member(client: FlaskClient, mock_member_repo: MemberRepository):
    mock_member_repo.get_member_by_username.return_value = not None
    mock_member_repo.delete_member.return_value = base_member["username"]
    rsp = client.delete(f"/members/{base_member['username']}")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["username"] == base_member["username"]

