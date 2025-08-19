import pytest

from flask.testing import FlaskClient

from app import create_app

from app.extensions import db
from app.config import Config

from app.models.member_model import Member

sysadmin_member = {
    "username": "sysadmin",
    "password": "password",
    "roles": ["sysadmin"],
    "name": "sysadmin",
    "email": "email,"
}

fenix_auth_member = {
    "username": "fenixuser",
    "ist_id": "ist100000",
    "roles": ["sysadmin"],
    "name": "sysadmin",
    "email": "email,"
}

@pytest.fixture()
def client():
    Config.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    Config.SESSION_TYPE = "cachelib"
    Config.ENABLED_ACCESS_CONTROL = "True"
    app = create_app()

    with app.app_context():
        db.create_all()
        db.session.add(Member(**sysadmin_member))
        db.session.add(Member(**fenix_auth_member))
        db.session.commit()
        yield app.test_client()
        db.drop_all()

def test_invalid_login_username(client: FlaskClient):
    rsp = client.post("/login", json={"username": "invalidname", "password": "password"})
    assert rsp.status_code == 401

def test_invalid_login_password(client: FlaskClient):
    rsp = client.post("/login", json={"username": "sysadmin", "password": "invalid_password"})
    assert rsp.status_code == 401

def test_login_sysadmin(client: FlaskClient):
    with client.session_transaction() as session:
        assert not "id" in session

    rsp = client.post("/login", json={"username": "sysadmin", "password": "password"})
    with client.session_transaction() as session:
        assert "id" in session

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"

    assert "description" in rsp.json and rsp.json["description"] == "Logged in successfully!"
    assert "member" in rsp.json and "username" in rsp.json["member"] and rsp.json["member"]["username"] == "sysadmin"

def test_login_fenix_auth_member(client: FlaskClient):
    with client.session_transaction() as session:
        assert not "id" in session

    rsp = client.post("/login", json={"username": "fenixuser", "password": "password"})
    assert rsp.status_code == 401
    with client.session_transaction() as session:
        assert not "id" in session


def test_logout(client: FlaskClient):
    with client.session_transaction() as session:
        assert "id" not in session
    rsp = client.post("/login", json={"username": "sysadmin", "password": "password"})
    with client.session_transaction() as session:
        assert "id" in session
    assert rsp.status_code == 200
    rsp = client.get("/logout")
    with client.session_transaction() as session:
        assert "id" not in session
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert "username" in rsp.json and rsp.json["username"] == "sysadmin"
    assert "description" in rsp.json and "Logout successful!" in rsp.json["description"]

def test_login_me(client: FlaskClient):
    with client.session_transaction() as session:
        assert not "id" in session
    rsp = client.post("/login", json={"username": "sysadmin", "password": "password"})
    with client.session_transaction() as session:
        assert "id" in session
    assert rsp.status_code == 200

    rsp = client.get("/me")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    items = {**sysadmin_member}
    del items["password"]
    for k in items:
        assert rsp.json[k] == sysadmin_member[k]
