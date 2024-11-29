from functools import wraps
from http import HTTPStatus
from typing import List
import inspect

from flask import abort, session

from app.services.projects import project_service
from app.services.roles import roles_service


def requires_login(f):
    """Decorator to enforce a user has a valid session."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get("username", "")
        if not username:
            abort(HTTPStatus.UNAUTHORIZED, description="No session")
        return f(*args, **kwargs)

    return decorated_function


def requires_permission(allow_self_action=False, **permissions_by_scope):
    for scope, permissions in permissions_by_scope.items():
        if not roles_service.exists_scope(scope):
            raise PermissionError(f"Invalid scope '{scope}', doesn't exist")

        if not isinstance(permissions, list):
            raise PermissionError(
                f"Invalid permissions value for scope '{scope}', expected list, got {type(permissions)}"
            )

    def decorator(f):
        # evaluate function signature to determine if flag is valid
        if allow_self_action:
            if "username" not in inspect.signature(f).parameters.keys():
                raise PermissionError(
                    f"{f.__name__}: allow_self_action used in handler that doesn't expect a 'username' argument"
                )

        @wraps(f)
        def wrapper(*args, **kwargs):
            if allow_self_action and (session.get("username", "") == kwargs.get("username", "_")):
                return f(*args, **kwargs)

            for scope, permissions in permissions_by_scope.items():
                validator = get_scope_validator(scope)
                if validator(permissions=permissions, **kwargs):
                    return f(*args, **kwargs)
            abort(HTTPStatus.UNAUTHORIZED, description="You don't have permissions to perform this action")

        return wrapper

    return decorator


def get_scope_validator(scope: str) -> callable:
    match scope:
        case "general":
            return validate_general_permission
        case "project":
            return validate_project_permission
        case _:
            return lambda *_, **__: False


def validate_general_permission(permissions: List[str]) -> bool:
    roles = session.get("roles", [])
    for perm in permissions:
        if roles_service.has_permission("general", roles, perm):
            return True
    return False


def validate_project_permission(permissions: List[str], project_name: str) -> bool:
    username = session.get("username", "")
    if username == "":
        return False

    roles = project_service.get_project_user_roles(username, project_name)
    for perm in permissions:
        if roles_service.has_permissions("project", roles, perm):
            return True
    return False
