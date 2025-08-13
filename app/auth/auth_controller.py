from http import HTTPStatus

from flask import session, abort, g
from functools import wraps

from app.auth.permission_strategies import Ctx, indexed_permission_evaluators, indexed_endpoint_validators
from app.auth.scopes.system_scopes import SystemScopes

from app.repositories.member_repository import MemberRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.project_repository import ProjectRepository

from app.schemas.member_schema import MemberSchema



class AuthController:
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
    :param project_repo: Repository interface to retrieve member data.
    :type project_repo: ``app.repositories.project_repository.ProjectRepository``
    :param participation_repo: Repository interface to retrieve member data.
    :type participation_repo: ``app.repositories.project_participation_repository.ProjectParticipationRepository``
    :param system_scopes: Class with system scopes.
    :type participation_repo: ``app.auth.scopes.system_scopes.SystemScopes``
    """

    def __init__(self, *, enabled: bool, member_repo: MemberRepository, project_repo: ProjectRepository, participation_repo: ProjectParticipationRepository,system_scopes: SystemScopes):
        self.enabled = enabled
        self.member_repo = member_repo
        self.project_repo = project_repo
        self.participation_repo = participation_repo
        self.system_scopes = system_scopes

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

        :param fn: Function that authenticates a user and returns its model.
        :type fn: function
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return abort(HTTPStatus.NOT_IMPLEMENTED)

            member = fn(*args, **kwargs)
            if member is None:
                return abort(HTTPStatus.UNAUTHORIZED)
            session["id"] = member.id
            return {"message": "Logged in successfully!", "member": MemberSchema.from_member(member).model_dump(exclude="password")}
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

        :param fn: Decorated controller.
        :type fn: function
        """

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return fn(*args, **kwargs)
            if "id" not in session:
                return abort(HTTPStatus.UNAUTHORIZED, description="You are not logged in")
            member = self.member_repo.get_member_by_id(session["id"])
            if member is None:  # member deleted while session was still valid
                return abort(HTTPStatus.UNAUTHORIZED, description="You are not logged in")
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
                return abort(HTTPStatus.NOT_IMPLEMENTED)
            r = fn(*args, **kwargs)
            session.clear()
            g.current_member = None
            return r

        return wrapper

    def requires_permission(self, **scoped_permissions):
        """
        Decorator to enforce scoped permission checks on route handlers.

        Example::

            @bp.route("/projects/<name>", methods=["PUT"])
            @requires_permission(general="project:update", project="edit")
            def update_project(name):
                pass

        Each keyword argument represents a scope, and its value is the required permission
        for that scope. If any one scope grants the required permission, access is allowed.

        :param scoped_permissions: Mapping of scope names to required permission strings.
        :type scoped_permissions: dict[str, str]

        :raises ValueError: If an undefined scope is passed.
        :raises ValueError: If and undefined permission is passed for the corresponding scope.
        """
        for scope in scoped_permissions:
            if self.system_scopes.get_scope(scope) is None or scope not in indexed_permission_evaluators:
                raise ValueError(f"Undefined scope or permission evaluator for scope '{scope}'")

            permission = scoped_permissions[scope]
            for role in self.system_scopes.get_scope(scope).roles:
                if permission in role.permissions:
                    break
            else:
                raise ValueError(f"Undefined permission '{permission}' in any role for scope '{scope}'")

        def decorator(fn):
            for scope in scoped_permissions:
                assert_valid_endpoint = indexed_endpoint_validators[scope]
                assert_valid_endpoint(fn) # raises error if invalid endpoint signature

            @wraps(fn)
            @self.requires_login
            def wrapper(*args, **kwargs):
                # skip authorization if access control is disabled
                if not self.enabled:
                    return fn(*args, **kwargs)

                # check if user has at least permissions in one scope
                for scope in scoped_permissions:
                    has_perm_eval = indexed_permission_evaluators[scope]
                    if has_perm_eval(Ctx(authCtx=self, permission=scoped_permissions[scope], args=args, kwargs=kwargs)):
                        return fn(*args, **kwargs)
                return abort(HTTPStatus.FORBIDDEN, description="You don't have permissions to perform this action")

            return wrapper
        return decorator
