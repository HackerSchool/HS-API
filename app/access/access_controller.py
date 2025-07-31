import inspect
from http import HTTPStatus

from flask import session, abort, g
from functools import wraps

from app.access.utils import current_member
from app.repositories.member_repository import MemberRepository
from app.access.permissions.permission_handler import PermissionHandler
from app.schemas.member_schema import MemberSchema

class AccessController:
    """
    Enforces authentication and authorization on controllers using `flask-session`.

    This class provides decorators to:

    - Log in members via :func:`login_member`.
    - Log out members via :func:`logout_member`.
    - Enforce authentication on controllers via :func:`requires_login` and populate the ``current_member`` global proxy.
    - Enforce authorization checks on controllers via ``requires_permission``. This also enforces authentication
      by using :func`requires_login`, making ``current_member`` also available.

    :param enabled: Flag to enable or disable access control enforcement.
    :type enabled: bool
    :param member_repo: Repository interface to retrieve member data.
    :type member_repo: ``app.repositories.member_repository.MemberRepository``
    :param permission_handler: Service that validates roles' permissions.
    :type permission_handler: ``app.access.permission_handler.PermissionHandler``
    """
    def __init__(self, *, enabled: bool, member_repo: MemberRepository, permission_handler: PermissionHandler):
        self.enabled = enabled
        self.member_repo = member_repo
        self.permission_handler = permission_handler

    def login_member(self, fn):
        """
        This is meant to act as the controller to start member sessions. Should be used to decorate functions that authenticate
        a member and return it to start the session.
        It's not a controller decorator, it is the controller, the functions should simply provide the member model.

        Example::

            @app.route("login/")
            @login_member
            def login():
                return Member() # return the authenticated member here

            @app.route("oauth-callback/")
            @login_member
            def oauth_callback():
                return Member()

        :param fn: Authentication function
        :return func:
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return abort(HTTPStatus.NOT_FOUND)

            member = fn(*args, **kwargs)
            if member is None:
                return abort(HTTPStatus.UNAUTHORIZED)
            session["id"] = member.id
            return {"message": "Logged in successfully!", "member": MemberSchema.from_member(member).model_dump()}
        return wrapper

    def requires_login(self, fn):
        """
        Decorate controllers that require a logged-in user.
        This decorator enables ``current_member`` global to be accessed in controllers.

        Example::
            from app.access import current_member

            @bp.route("/members/<username>", methods=["PUT"])
            @requires_login
            def update_member(username):
                if current_member.username == username:
                    pass
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return fn(*args, **kwargs)
            if "id" not in session:
                return abort(HTTPStatus.UNAUTHORIZED)
            member = self.member_repo.get_member_by_id(session["id"])
            if member is None: # member deleted while session was still valid
                return abort(HTTPStatus.UNAUTHORIZED)
            g.current_member = member
            return fn(*args, **kwargs)
        return wrapper

    def logout_member(self, fn):
        """
        Decorate controllers meant to end a user session.
        Example::

            @app.route("login/")
            @access_controller.logout_member
            def logout():
                return {"message": "Logged out successfully!"}

        :param fn: Decorated controller.
        :type fn: function
        """
        @wraps(fn)
        @self.requires_login
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return abort(HTTPStatus.NOT_FOUND)
            r = fn(*args, **kwargs)
            session.clear()
            g.current_member = None
            return r
        return wrapper


    def requires_permission(self, *, allow_self_action=False, **scopes_permissions):
        """
        Decorator to enforce scoped permission checks on route handlers.

        Example::

            @bp.route("/projects/<name>", methods=["PUT"])
            @requires_permission(general="project:update", project="project:update")
            def update_project(name):
                pass

        Each keyword argument represents a scope, and its value is the required permission
        for that scope. If any one scope grants the required permission, access is allowed.

        If ``allow_self_action`` is True, and the route includes a ``username`` argument,
        the current member is allowed to proceed without matching a permission if the
        ``username`` matches their own.

        :param allow_self_action: If True, allows the current user to act on their own resource
            when a ``username`` parameter is present and matches their identity.
        :type allow_self_action: bool

        :param scopes_permissions: Mapping of scope names to required permission strings.
            Example: ``general="member:update"``, ``project="project:delete"``
        :type scopes_permissions: dict[str, str]

        :raises ValueError: If an undefined scope is passed.
        :raises ValueError: If ``allow_self_action`` is set but the controller does not accept a ``username`` parameter.
        """
        for scope in scopes_permissions:
            if not self.permission_handler.system_scopes.get_scope(scope):
                raise ValueError(f'Undefined scope "{scope}"')

        def decorator(fn):
            if allow_self_action:
                if "username" not in inspect.signature(fn).parameters.keys():
                    raise ValueError(f'Usage of allow_self_action in controller without "username" parameter')

            @wraps(fn)
            @self.requires_login
            def wrapper(*args, **kwargs):
                # skip authorization if access control is disabled
                if not self.enabled:
                    return fn(*args, **kwargs)

                # skip if user performin self action
                if allow_self_action and kwargs["username"] == current_member.username:
                    return fn(*args, **kwargs)

                # check if user has at least permissions in one scope
                for scope in scopes_permissions:
                    roles_retrieval_fn = self.permission_handler.get_scope_retrieval_strategy(scope)
                    roles = roles_retrieval_fn(self, *args, **kwargs)
                    if self.permission_handler.has_permission(scope_name=scope, permission=scopes_permissions[scope], subject_roles=roles):
                        return fn(*args, **kwargs)
                return abort(HTTPStatus.UNAUTHORIZED)
            return wrapper
        return decorator
