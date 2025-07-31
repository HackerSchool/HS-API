import pytest
import os

from app.access.permissions.permission_handler import PermissionHandler

@pytest.fixture()
def permission_handler():
    yield PermissionHandler.from_yaml_config(
        os.path.join(os.path.dirname(__file__), "roles_test.yaml")
    )

def test_has_permission_valid(permission_handler: PermissionHandler):
    assert permission_handler.has_permission(scope_name="general", permission="member:read", subject_roles=["sysadmin"])

def test_has_permission_invalid(permission_handler: PermissionHandler):
    assert not permission_handler.has_permission(scope_name="general", permission="member:create", subject_roles=["lab"])

def test_is_permission_in_scope_valid(permission_handler: PermissionHandler):
    assert permission_handler.is_permission_in_scope(scope_name="general", permission="member:read")

def test_is_permission_in_scope_invalid(permission_handler: PermissionHandler):
    assert not permission_handler.is_permission_in_scope(scope_name="project", permission="member:read")

def test_has_priority_invalid(permission_handler: PermissionHandler):
    assert permission_handler.has_priority(scope_name="general", subject_roles=["money"], target_roles=["lab"]) is False

def test_has_priority_invalid(permission_handler: PermissionHandler):
    assert permission_handler.has_priority(scope_name="general", subject_roles=["sysadmin"], target_roles=["lab"]) is True
