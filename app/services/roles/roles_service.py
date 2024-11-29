import json
from typing import Set, Tuple, List

# scopes are indexed by name, each value is a dictinoary that indexes level and permissions of a role by name
__scopes: dict[str : dict[str : Tuple[int, Set[str]]]] = None


def exists_scope(scope: str) -> bool:
    return scope in __scopes.keys()


def exists_role_in_scope(scope: str, role: str) -> bool:
    if scope not in __scopes.keys():
        return False

    return role in __scopes[scope]


def has_permission(scope: str, roles: List[str], permission):
    for role in roles:
        if permission in _get_role_permissions(scope, role):
            return True
    return False


def has_higher_level(scope: str, roles: List[str], role):
    _, highest_lvl = _get_highest(scope, roles)
    if highest_lvl == 0:
        return highest_lvl <= _get_role_level(scope, role)
    return highest_lvl < _get_role_level(scope, role)  # < instead of <= means we cannot add "horizontally"


def _get_role_level(scope: str, role: str) -> int:
    """
    Returns `role` level in given `scope`.
    If scope doesn't exist or role doesn't exist in scope returns -1.
    """
    return __scopes.get(scope, dict()).get(role, (-1, None))[0]


def _get_role_permissions(scope: str, role: str):
    """
    Returns `role` permissions in given `scope`.
    If scope doesn't exist or role doesn't exist in scope returns 99.
    """
    return __scopes.get(scope, dict()).get(role, (99, set()))[1]


def _get_highest(scope: str, roles_list: list) -> Tuple[str, int]:
    """returns highest role and level in `roles_list`"""
    highest_lvl = 99
    highest_role = ""
    for role in roles_list:
        tag_lvl = _get_role_level(scope, role)
        if tag_lvl < highest_lvl:
            highest_lvl = tag_lvl
            highest_role = role

    return highest_role, highest_lvl


def init_app(app) -> None:
    global __scopes
    # get configuration
    file_path = app.config.get("ROLES_PATH", "")
    if file_path == "":
        app.logger.error("ROLES_PATH environment not set")
        raise KeyError

    # load scopes
    # load roles
    jsonData: any
    try:
        with open(file_path, "r") as f:
            jsonData = json.load(f)
    except FileNotFoundError:
        app.logger.error(f"Roles file {file_path} not found")
        raise
    except Exception:
        app.logger.error(f"Failed reading roles from file {file_path}")
        raise

    scopes = jsonData.get("scopes", "")
    if scopes == "":
        raise KeyError("Missing 'scopes' key")

    if not isinstance(scopes, list):
        raise ValueError(f"Invalid 'scopes' key value, expected list got {type(scopes)}")

    scopesDict = {}
    for scope in scopes:
        if not isinstance(scope, dict):
            raise ValueError(f"Invalid scope entry type, expected JSON object got {type(scope)}")

        scope_name = scope.get("name", "")
        if scope_name == "":
            raise KeyError("Missing 'name' key in scope entry")
        if not isinstance(scope_name, str):
            raise ValueError(f"Invalid 'name' key value type in scope, expected string got {type(scope_name)}")

        roles = scope.get("roles", "")
        if roles == "":
            raise KeyError("roles")
        if not isinstance(roles, list):
            raise ValueError("roles key")

        app.logger.info(f"Detecting roles in scope {scope_name}:")
        # validate roles
        rolesDict = {}
        for role in roles:
            if not isinstance(role, dict):
                raise ValueError(f"Invalid role entry type, expected JSON object got {type(role)}")

            role_name = role.get("name", "")
            if role_name == "":
                raise KeyError(f"Missing 'name' key in role entry in scope {scope_name}")
            if not isinstance(role_name, str):
                raise ValueError(
                    f"Invalid 'name' key value type in role entry in scope {scope_name}, expected string got {type(role_name)}"
                )

            permissions = role.get("permissions", "")
            if permissions == "":
                raise KeyError(f"Missing 'permissions' key in role entry '{role_name}' in scope '{scope_name}'")
            if not isinstance(permissions, list):
                raise ValueError(
                    f"Invalid 'permissions' key value type in role entry '{role_name}' in scope '{scope_name}', expected list got {type(permissions)}"
                )

            level = role.get("level", "")
            if level == "":
                raise KeyError(f"Missing 'level' key in role entry {role_name} in scope {scope_name}")
            if not isinstance(level, int):
                raise ValueError(
                    f"Invalid 'level' key value type in role entry '{role_name}' in scope '{scope_name}', expected int got {type(level)}"
                )

            rolesDict[role_name] = (level, set(permissions))
            app.logger.info(f"* {role['name']}")
        scopesDict[scope_name] = rolesDict
    __scopes = scopesDict
