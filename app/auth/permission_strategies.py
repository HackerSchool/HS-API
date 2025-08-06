from typing import List, Dict, TYPE_CHECKING

from dataclasses import dataclass

from app.auth.utils import current_member

if TYPE_CHECKING:
    from app.auth.auth_controller import AuthController

@dataclass
class Ctx:
    accessCtx: "AuthController"
    permission: str
    args: List[str]
    kwargs: Dict[str, str]

def general_scope_evaluator(ctx: Ctx) -> bool:
    # if performing self action
    if "member" in ctx.permission and "username" in ctx.kwargs and ctx.kwargs[
        "username"] == current_member.username:
        return True

    scope = ctx.accessCtx.system_scopes.get_scope("general")
    for role in current_member.roles:
        if ctx.permission in scope.get_role(role).permissions:
            return True
    return False

def project_scope_evaluator(ctx: Ctx):
    pass


def workshop_scope_evaluator(ctx: Ctx):
    pass


indexed_permission_evaluators = {
    "general": general_scope_evaluator,
    "project": project_scope_evaluator,
    "workshop": workshop_scope_evaluator,
}
