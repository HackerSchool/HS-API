import pytest

from unittest.mock import MagicMock

from app.utils import ProjectStateEnum

base_member = {
    "username": "username",
    "name": "name",
    "email": "email",
}

base_project = {
    "name": "proj_name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE
}

base_participation = {
    "join_date": "1970-01-01"
}

@pytest.fixture
def mock_member_repo():
    return MagicMock()

@pytest.fixture
def mock_system_roles():
    return MagicMock()

@pytest.fixture
def client(mock_member_repo):
    from app.config import Config
    Config.ENABLED_ACCESS_CONTROL = False

    app = create_app(member_repo=mock_member_repo)
    with app.test_client() as client:
        yield client
