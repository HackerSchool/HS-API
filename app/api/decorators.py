from functools import wraps

from flask import session
from http import HTTPStatus

from app.extensions import roles_handler
from app.api.errors import throw_api_error

def requires_login(f):
    """ Decorator to enforce a user has a valid session. """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', '')
        if not username:
            throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Unauthenticated, please log in"})
        return f(*args, **kwargs)
    return decorated_function

def requires_permission(*permissions: str, allow_self_action : bool = False):
    """
    Decorator to enforce permission requirements for endpoints.

    This decorator checks if the user associated with the current session
    has the specified permission. If the endpoint is designed to allow 
    users to perform actions on their own accounts, it grants access 
    without further validation. For other actions, it checks if the user 
    has the necessary permissions defined by their roles in the session.

    :args:
        permission (list): Required permissions to access the decorated endpoint.
        allow_self_action (bool): If the user can perform action in itself despite not having permissions.

    .. example::
        .. code-block:: python
        # Endpoint where members can edit their own users
        @bp.route('/<string:member_username>', methods=['PUT'])
        @requires_login
        @requires_permission('update member')
        def update_member(member_username):
            pass

        .. code-block:: python

        @bp.route('/<string>:project_name>', methods=['DELETE'])
        @requires_login
        @requires_permission('delete project')
        def delete_member(project_name):
            pass

    :notes:
        - The kwarg `username` must be declared on the decorated function
            to allow users to perform actions without the necessary permission 
        - If the username kwarg (<username> defined in the Flask route path) matches
            the username in the session, the user is allowed to perform any action.
        - This decorator is intended to be used on endpoints where 
            permission checks are necessary based on user roles and actions.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            member_username = kwargs.get('username', '')
            # Members can perform actions on their own user
            if allow_self_action and member_username:
                if session.get("username", "") == member_username:
                    return f(*args, **kwargs)
            # Validate external users
            roles = session.get('roles', '')
            for perm in permissions:
                if not roles_handler.has_permission(roles, perm):
                    throw_api_error(HTTPStatus.FORBIDDEN, {"error": f"You don't have permission to {perm}"})
            return f(*args, **kwargs)

        return wrapper
    return decorator