from http import HTTPStatus
from types import new_class

import pytest

from flask.testing import FlaskClient
from flask import Flask

from app import create_app
from app.extensions import db
from app.config import Config
from app.models.member_model import Member

base_member = {
    "username": "baseusername",
    "name": "name",
    "email": "email",
}

roles = ["sysadmin", "dev", "finance", "member"]

def populate_db():
    for i, role in enumerate(roles):
        new_member = {
            "username": role,
            "password": "password",
            "name": role,
            "email": role,
            "ist_id": "ist10000" + str(i),
            "roles": [role]
        }
        member = Member(**new_member)
        db.session.add(member)
    db.session.commit()

@pytest.fixture()
def app():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    Config.SESSION_TYPE = "cachelib"
    Config.ENABLED_ACCESS_CONTROL = "True"
    app = create_app()

    with app.app_context():
        db.create_all()
        populate_db()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def logged_in_sysadmin(app: Flask):
    with app.test_client() as client:
        client.post("/login", json={"username": "sysadmin", "password": "password"})
        yield client

@pytest.fixture(scope="function")
def logged_in_dev(app: Flask):
    with app.test_client() as client:
        client.post("/login", json={"username": "dev", "password": "password"})
        yield client

@pytest.fixture(scope="function")
def logged_in_member(app: Flask):
    with app.test_client() as client:
        client.post("/login", json={"username": "member", "password": "password"})
        yield client

def test_sysadmin_create_member(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.post("/members", json={**base_member, "roles": ["member"]})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k in base_member:
        assert rsp.json[k] == base_member[k]

def test_sysadmin_create_sysadmin(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.post("/members", json={**base_member, "roles": ["sysadmin"]})
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_member_create_member(logged_in_member: FlaskClient):
    rsp = logged_in_member.post("/members", json={**base_member, "roles": ["member"]})
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_dev_create_admin(logged_in_dev: FlaskClient):
    rsp = logged_in_dev.post("/members", json={**base_member, "roles": ["sysadmin"]})
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_dev_create_dev(logged_in_dev: FlaskClient):
    rsp = logged_in_dev.post("/members", json={**base_member, "roles": ["dev"]})
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_dev_create_duplicate_username(logged_in_dev: FlaskClient):
    rsp = logged_in_dev.post("/members", json={**base_member, "roles": ["member"]})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"

    rsp = logged_in_dev.post("/members", json={**base_member, "roles": ["member"]})
    assert rsp.status_code == HTTPStatus.CONFLICT

def test_dev_create_duplicate_ist_ist_id(logged_in_dev: FlaskClient):
    info = {**base_member, "ist_id": "ist1100000", "roles": ["member"]}

    rsp = logged_in_dev.post("/members", json=info)
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"

    rsp = logged_in_dev.post("/members", json=info)
    assert rsp.status_code == HTTPStatus.CONFLICT

def test_sysadmin_get_members(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.get("/members")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert isinstance(rsp.json, list) and len(rsp.json) == len(roles)
    for m in rsp.json:
        assert m["username"] in roles
        assert m["name"] in roles
        assert m["email"] in roles

@pytest.mark.parametrize("role", roles)
def test_sysadmin_get_member(logged_in_sysadmin: FlaskClient, role):
    rsp = logged_in_sysadmin.get(f"/members/{role}")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == role
    assert "email" in rsp.json and rsp.json["username"] == role
    assert "name" in rsp.json and rsp.json["username"] == role
    assert "roles" in rsp.json and rsp.json["roles"] == [role]

def test_sysadmin_get_member_no_exist(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.get(f"/members/no_exist")
    assert rsp.status_code == 404

@pytest.mark.parametrize("role", {*roles} - {"sysadmin"})
def test_sysadmin_updates_inferior_roles(logged_in_sysadmin: FlaskClient, role):
    rsp = logged_in_sysadmin.put(f"/members/{role}", json={"username": "newname"})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == "newname"
    assert "roles" in rsp.json and rsp.json["roles"] == [role]

def test_sysadmin_updates_own_roles(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put(f"/members/sysadmin", json={"roles": ["dev", "member"]})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "roles" in rsp.json and rsp.json["roles"] == ["dev", "member"]

def test_sysadmin_update_member_no_exist(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put(f"/members/no_exist", json={"username": "newname"})
    assert rsp.status_code == 404

def test_sysadmin_update_member_conflict(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put(f"/members/member", json={"username": "dev"})
    assert rsp.status_code == HTTPStatus.CONFLICT

def test_member_updates_themselves_valid(logged_in_member: FlaskClient):
    rsp = logged_in_member.put(f"/members/member", json={"username": "newname"})
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == "newname"

def test_member_updates_themselves_roles_invalid(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.put("/members/member", json={"roles": ["dev"]})
    assert rsp.status_code == 200

def test_same_priority_edit_invalid(logged_in_dev: FlaskClient):
    db.session.add(Member(**{**base_member, "roles": ["dev"]}))
    db.session.commit()
    rsp = logged_in_dev.put(f'/members/{base_member["username"]}', json={"username": "anothername"})
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_dev_updates_themselves_roles_invalid(logged_in_dev: FlaskClient):
    rsp = logged_in_dev.put('/members/dev', json={"roles": ["sysadmin"]})
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_sysadmin_delete_member(logged_in_sysadmin: FlaskClient):
    rsp = logged_in_sysadmin.delete("/members/member")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == "member"

def test_member_delete_dev(logged_in_member: FlaskClient):
    rsp = logged_in_member.delete("/members/dev")
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_member_delete_themselves(logged_in_member: FlaskClient):
    rsp = logged_in_member.delete("/members/member")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == "member"

def test_dev_delete_sysadmin(logged_in_dev: FlaskClient):
    rsp = logged_in_dev.delete("/members/sysadmin")
    assert rsp.status_code == HTTPStatus.FORBIDDEN

def test_dev_delete_no_exist(logged_in_dev: FlaskClient):
    rsp = logged_in_dev.delete("/members/no_exist")
    assert rsp.status_code == HTTPStatus.NOT_FOUND
