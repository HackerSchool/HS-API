import pytest
from unittest.mock import Mock

from app.services.roles import roles_service


def test_load_invalid_config():
    mock_app = Mock()
    mock_app.config = {"ROLES_PATH": "tests/services/assets/no_file.json"}
    with pytest.raises(FileNotFoundError) as e_info:
        roles_service.init_app(mock_app)

    assert e_info.match("no_file.json") is True


@pytest.fixture
def load_config():
    mock_app = Mock()
    mock_app.config = {"ROLES_PATH": "tests/services/assets/roles_test.json"}
    roles_service.init_app(mock_app)


def test_config_loaded(load_config):
    assert roles_service.__scopes == {
        "general": {"admin": (0, {"create", "read", "update", "delete"}), "member": (1, {"read"})},
        "project": {"coordinator": (0, {"update", "add participant", "remove participant"}), "participant": (1, set())},
    }


def test_exists_scope_true():
    assert roles_service.exists_scope("general") is True
    assert roles_service.exists_scope("project") is True


def test_exists_scope_false():
    assert roles_service.exists_scope("scope invalid") is False
    assert roles_service.exists_scope(1) is False
    assert roles_service.exists_scope(True) is False
    assert roles_service.exists_scope("") is False


def test_exists_role_in_scope_true():
    assert roles_service.exists_role_in_scope("general", "admin") is True
    assert roles_service.exists_role_in_scope("general", "member") is True
    assert roles_service.exists_role_in_scope("project", "coordinator") is True
    assert roles_service.exists_role_in_scope("project", "participant") is True


def test_exists_role_in_scope_false():
    assert roles_service.exists_role_in_scope("scope invalid", "role invalid") is False
    assert roles_service.exists_role_in_scope("scope invalid", "member") is False
    assert roles_service.exists_role_in_scope("general", "role invalid") is False

    assert roles_service.exists_role_in_scope("", "") is False
    assert roles_service.exists_role_in_scope("general", "") is False
    assert roles_service.exists_role_in_scope("", "member") is False


def test_has_permission_true():
    assert roles_service.has_permission("general", ["admin"], "create") is True
    assert roles_service.has_permission("general", ["admin"], "update") is True
    assert roles_service.has_permission("general", ["admin"], "delete") is True
    assert roles_service.has_permission("general", ["member"], "read") is True
    assert roles_service.has_permission("project", ["coordinator"], "update") is True
    assert roles_service.has_permission("project", ["coordinator"], "add participant") is True
    assert roles_service.has_permission("project", ["coordinator"], "remove participant") is True
    assert roles_service.has_permission("project", ["coordinator"], "remove participant") is True
    assert roles_service.has_permission("project", ["coordinator", "participant"], "remove participant") is True


def test_has_permission_false():
    assert roles_service.has_permission("invalid scope", ["invalid role"], "invalid permission") is False
    assert roles_service.has_permission("general", ["invalid role"], "invalid permission") is False
    assert roles_service.has_permission("general", ["admin"], "invalid permission") is False
    assert roles_service.has_permission("general", [], "read") is False

    assert roles_service.has_permission("project", ["participant"], "update") is False


def test_has_higher_level_true():
    assert roles_service.has_higher_level("general", ["admin"], "member") is True
    assert roles_service.has_higher_level("general", ["admin"], "member") is True
    assert roles_service.has_higher_level("general", ["admin"], "admin") is True  # level 0 has all
    assert roles_service.has_higher_level("general", ["admin", "member"], "admin") is True  # level 0 has all


def test_has_higher_level_false():
    assert roles_service.has_higher_level("general", ["member"], "member") is False
    assert roles_service.has_higher_level("general", ["member"], "member") is False
    assert roles_service.has_higher_level("general", ["member"], "admin") is False
    assert roles_service.has_higher_level("", ["admin", "member"], "member") is False
    assert roles_service.has_higher_level("general", [], "member") is False
    assert roles_service.has_higher_level("general", [], "") is False
    assert roles_service.has_higher_level("general", ["member"], "") is False
    assert roles_service.has_higher_level("general", ["admin"], "") is False
