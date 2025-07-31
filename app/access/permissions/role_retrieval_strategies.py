from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.access import AccessController

from app.access.utils import current_member

def get_general_roles(ctx: "AccessController", **kwargs) -> List[str]:
    """
    Retrieves roles directly from the current_member (for general permissions).
    """
    if current_member:
        return current_member.roles
    return []

def get_project_roles(ctx: "AccessController", **kwargs) -> List[str]:
    """ NOT IMPLEMENTED """
    return ["coordinator"]

def get_workshop_roles(ctx: "AccessController", **kwargs) -> List[str]:
    """ NOT IMPLEMENTED """
    return []

indexed_strategies = {
    "general": get_general_roles,
    "project": get_project_roles,
    "workshop": get_workshop_roles
}
