import pytest
from flask.testing import FlaskClient

from app import create_app
from app.extensions import db
from app.config import Config
from app.models.member_model import Member

base_member = {
    "ist_id": "ist100000",
    "name": "name",
    "username": "username",
    "email": "email",
}

@pytest.fixture(scope="function")
def client():
    config = Config
    config.DATABASE_PATH = "sqlite:///:memory:"
    config.SESSION_TYPE = "cachelib"
    app = create_app(config)

    with app.app_context():
        # TODO add auth logic once added
        db.create_all()
        populate_db()
        yield app.test_client()
        db.drop_all()


def populate_db():
    for i in range(5):
        new_member = {}
        for k, v in base_member.items():
            new_member[k] = base_member[k] + str(i)
        member = Member(**new_member)
        db.session.add(member)
    db.session.commit()


#def test_get_member(client: FlaskClient):
#    rsp = client.get(f"/members/{base_member['ist_id'] + str(0)}")
#    assert rsp.status_code == 200
#    assert rsp.mimetype == "application/json"
#    assert ("name", "email", "username", "ist_id") - rsp.json.keys() == set()
#    for k, v in base_member.items():
#        assert rsp.json[k] == v + str(0)
#
#