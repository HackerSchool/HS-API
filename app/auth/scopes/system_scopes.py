import logging

from typing import List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

class Role(BaseModel):
    """
    Represents a role within a scope, defining its name, privilege level, and permissions.

    :param name: The unique name of the role.
    :type name: str
    :param privilege: The privilege level of the role, must be greater than zero.
    :type privilege: int
    :param permissions: Optional list of permissions assigned to this role.
    :type permissions: Optional[List[str]]
    """
    name: str = Field(...)
    privilege: int = Field(..., gt=0)
    permissions: Optional[List[str]] = Field(...)

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v):
        if v is None:
            return []
        return v


class Scope(BaseModel):
    """
    Defines a scope which contains multiple roles.

    :param name: The name of the scope.
    :type name: str
    :param roles: A list of roles defined within this scope.
    :type roles: List[Role]
    """
    name: str = Field(...)
    roles: List[Role] = Field(default=[])

    def get_role(self, role_name: str) -> Optional[Role]:
        """
        Retrieve a role by its name within this scope.

        :param role_name: The name of the role to find.
        :type role_name: str
        :return: The matching :class:`Role` instance, or ``None`` if not found.
        :rtype: Role or None
        """
        for role in self.roles:
            if role.name == role_name:
                return role
        logger.warning(f'Unknown role used "{role_name}"')
        return None

class SystemScopes(BaseModel):
    """
    Container for all defined scopes in the system.

    :param scopes: A list of all scopes available.
    :type scopes: List[Scope]
    """
    scopes: List[Scope] = Field(...)

    def get_scope(self, scope_name: str) -> Optional[Scope]:
        """
        Retrieve a :class:`Scope` by its name or ``None``.

        :param scope_name: The name of the scope to look for.
        :type scope_name: str
        :return: The matching :class:`Scope` instance or ``None`` if not found.
        :rtype: Scope or None
        """
        for scope in self.scopes:
            if scope.name == scope_name:
                return scope
        logger.warning(f'Unknown scope used "{scope_name}"')
        return None

    def has_priority(self, scope_name: str, subject_roles: str, target_roles: str):
        if (scope := self.get_scope(scope_name)) is None:
            return False

        subject_roles = [r for role in subject_roles if (r := scope.get_role(role)) is not None]
        target_roles = [r for role in target_roles if (r := scope.get_role(role)) is not None]

        if len(subject_roles) == 0:
            return False
        if len(target_roles) == 0:
            return True

        highest_subject_role = max(subject_roles, key=lambda x: x.privilege)
        highest_target_role = max(target_roles, key=lambda x: x.privilege)
        return highest_subject_role.privilege > highest_target_role.privilege

    @classmethod
    def from_yaml_config(cls, path: str):
        """
        Create an instance from a YAML configuration file.

        :param path: Path to YAML configuration file.
        :type path: str
        :return: An instance of the class initialized with the parsed configuration.
        :rtype: :class:`PermissionHandler`
        """
        with open(path, "r") as f:
            return cls(**yaml.safe_load(f))
