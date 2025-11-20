import inspect

from dataclasses import dataclass

from typing import List, Dict, TYPE_CHECKING

from app.auth.utils import current_member

if TYPE_CHECKING:
    from app.auth.auth_controller import AuthController


@dataclass
class Ctx:
    authCtx: "AuthController"
    permission: str
    args: List[str]
    kwargs: Dict[str, str]


def general_scope_evaluator(ctx: Ctx) -> bool:
    # if performing self action
    if "member" in ctx.permission and "username" in ctx.kwargs and ctx.kwargs[
        "username"] == current_member.username:
        return True

    scope = ctx.authCtx.system_scopes.get_scope("general")
    for role in current_member.roles:
        if ctx.permission in scope.get_role(role).permissions:
            return True
    return False

def assert_valid_general_scope_endpoint(fn) -> None:
    """ Validates the controller function for the evaluator """
    pass

def project_scope_evaluator(ctx: Ctx):
    # if performing self action
    if "username" in ctx.kwargs and ctx.kwargs[
        "username"] == current_member.username:
        return True

    if (project := ctx.authCtx.project_repo.get_project_by_slug(ctx.kwargs["slug"])) is None:
        return False

    part = ctx.authCtx.participation_repo.get_participation_by_project_and_member_id(member_id=current_member.id, project_id=project.id)
    if part is None:
        return False

    scope = ctx.authCtx.system_scopes.get_scope("project")
    for role in part.roles:
        if ctx.permission in scope.get_role(role).permissions:
            return True
    return False

def assert_valid_project_scope_endpoint(fn) -> None:
    """ Validates the controller function for the evaluator """
    sig = inspect.signature(fn)
    if "slug" not in sig.parameters:
        raise ValueError(f'Missing argument "slug" in endpoint "{fn.__name__}"')

indexed_permission_evaluators = {
    "general": general_scope_evaluator,
    "project": project_scope_evaluator,
}

indexed_endpoint_validators = {
    "general": assert_valid_general_scope_endpoint,
    "project": assert_valid_project_scope_endpoint
}
