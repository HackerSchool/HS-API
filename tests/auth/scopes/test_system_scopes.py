import pytest

import os

from app.auth.scopes.system_scopes import SystemScopes

@pytest.fixture
def system_scopes():
    roles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roles_test.yaml")
    return SystemScopes.from_yaml_config(roles_path)

def test_has_priority_admin_member(system_scopes: SystemScopes):
    assert system_scopes.has_priority("general", ["sysadmin"], ["finance"])

def test_has_priority_member_admin(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("general", ["finance"], ["sysadmin"])

def test_has_priority_admin_admin(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("general", ["finance"], ["sysadmin"])

def test_has_priority_invalid_scope(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("invalid_scope", ["sysadmin"], ["sysadmin"])

def test_has_priority_invalid_subject_role(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("general", ["invalid_role"], ["sysadmin"])

def test_has_priority_invalid_target_role(system_scopes: SystemScopes):
    assert system_scopes.has_priority("general", ["sysadmin"], ["invalid_role"])

def test_has_priority_empty_subject_role(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("general", [], ["invalid_role"])

def test_has_priority_empty_target_role(system_scopes: SystemScopes):
    assert system_scopes.has_priority("general", ["sysadmin"], [])

def test_has_priority_multiple_roles_true(system_scopes: SystemScopes):
    assert system_scopes.has_priority("general", ["sysadmin", "member"], ["member"])

def test_has_priority_multiple_roles_false(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("general", ["sysadmin", "member"], ["member", "sysadmin"])

def test_has_priority_multiple_roles_invalid_true(system_scopes: SystemScopes):
    assert system_scopes.has_priority("general", ["sysadmin", "invalid_role", "invalid_role_2", "member"], ["invalid_role_1", "invalid_role_0"])

def test_has_priority_multiple_roles_invalid_false(system_scopes: SystemScopes):
    assert not system_scopes.has_priority("general", ["sysadmin", "invalid_role", "invalid_role_2", "member"], ["invalid_role_1", "invalid_role_0", "sysadmin"])




