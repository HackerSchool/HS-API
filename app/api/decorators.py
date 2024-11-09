from functools import wraps

from flask import session
from http import HTTPStatus

from app.extensions import tags_handler
from app.api.errors import throw_api_error

def requires_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', '')
        if not username:
            throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Unauthenticated, please log in"})
        return f(*args, **kwargs)
    return decorated_function


class InvalidPermissionError(Exception):
    def __init__(self, permission: str):
        """ Exception for unknown permission """
        super().__init__(f"Unkown permission {permission}")

def requires_permission(*permissions: str, allow_self_action : bool = False):
    """
    Decorator to enforce permission requirements for endpoints.

    This decorator checks if the user associated with the current session
    has the specified permission. If the endpoint is designed to allow 
    users to perform actions on their own accounts, it grants access 
    without further validation. For other actions, it checks if the user 
    has the necessary permissions defined by their tags in the session.

    :args:
        permission (str): The required permission to access the decorated endpoint.
        allow_self_action (bool): If the user can perform action in itself despite not having permissions.

    .. example::
        .. code-block:: python
        # Endpoint where members can edit their own users
        @bp.route('/<string:member_username>', methods=['PUT'])
        @login_required
        @required_permission('update_member')
        def update_member(member_username):
            pass

        .. code-block:: python

        @bp.route('/<string>:project_name>', methods=['DELETE'])
        @login_required
        @required_permission('delete_project')
        def delete_member(project_name):
            pass

    :notes:
        - The kwarg `member_username` must be declared on the decorated function
          to allow users to perform actions without the necessary permission 
        - If the member's username in the URL matches the username 
          in the session, the user is allowed to perform any action.
        - This decorator is intended to be used on endpoints where 
          permission checks are necessary based on user roles and actions.
    """
    for perm in permissions:
        if tags_handler.get_permission_err_message(perm) is None:
            raise InvalidPermissionError(perm)

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            member_username = kwargs.get('username', '')
            # Members can perform actions on their own user
            if allow_self_action and member_username:
                if session.get("username", "") == member_username:
                    return f(*args, **kwargs)
            # Validate external users
            tags = session.get('tags', '')
            for perm in permissions:
                if not tags_handler.can(tags, perm):
                    throw_api_error(HTTPStatus.FORBIDDEN, {"error": tags_handler.get_permission_err_message(perm)})
            return f(*args, **kwargs)

        return wrapper
    return decorator