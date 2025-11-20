
import pytest
import os

from flask import Flask

from app import create_app
from app.auth import AuthController
from app.auth.scopes.system_scopes import SystemScopes

roles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "./scopes/roles_test.yaml")

@pytest.fixture
def app():
    app = Flask(__name__)
    yield app

@pytest.fixture
def auth_controller():
    yield AuthController(enabled=True, member_repo=None, project_repo=None, participation_repo=None ,system_scopes=SystemScopes.from_yaml_config(roles_path))

def test_requires_permission_decorator_invalid_scope(app: Flask, auth_controller: AuthController):
    with pytest.raises(ValueError) as exc_info:
        @app.route("/login")
        @auth_controller.requires_permission(invalid_scope="read")
        def endpoint():
            pass

    assert "Undefined scope" in str(exc_info)

def test_requires_permission_decorator_invalid_permission(app: Flask, auth_controller: AuthController):
    with pytest.raises(ValueError) as exc_info:
        @app.route("/login")
        @auth_controller.requires_permission(general="invalid_perm")
        def endpoint():
            pass

    assert "Undefined permission" in str(exc_info)

def test_invalid_project_scope_endpoint(app: Flask, auth_controller: AuthController):
    with pytest.raises(ValueError) as exc_info:
        @app.route("/route")
        @auth_controller.requires_permission(project="update")
        def no_slug_endpoint():
            pass

    assert 'Missing argument "slug"' in str(exc_info)