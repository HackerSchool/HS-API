import logging

import yaml

from typing import List, Optional, Dict, Callable, Set
from pydantic import BaseModel, Field, field_validator

from app.access.permissions.role_retrieval_strategies import indexed_strategies


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

    def __gt__(self, other):
        if not isinstance(other, Role):
            return NotImplemented
        return self.privilege > other.privilege


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

    def get_role(self, role_name: str) -> Role | None:
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
        return None

    def get_role_permissions(self, role_name: str) -> List[str]:
        """
        Get the list of permissions assigned to a role by name.

        :param role_name: The name of the role.
        :type role_name: str
        :return: A list of permission strings assigned to the role, or empty list if role not found.
        :rtype: List[str]
        """
        if (role := self.get_role(role_name)) is None:
            return []
        return role.permissions


class SystemScopes(BaseModel):
    """
    Container for all defined scopes in the system.

    :param scopes: A list of all scopes available.
    :type scopes: List[Scope]
    """
    scopes: List[Scope] = Field(...)

    def get_scope(self, scope_name: str) -> Scope | None:
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
        return None


class PermissionHandler:
    """
    Handles permission and role-based access control across multiple scopes.

    This class provides utilities to:
    - Retrieve scopes by name.
    - Check whether a set of roles has specific permissions within a scope.
    - Compare role priorities between subjects and targets.
    - Load configurations from a YAML file via :meth:`from_yaml_config`.

    :ivar system_scopes: A list of all scopes used for permission and role evaluations.
    :vartype scopes: SystemScopes
    """
    def __init__(self, system_scopes: SystemScopes):
        self.system_scopes = system_scopes
        self.roles_retrieval_strategies: Dict[str, Callable] = {}

        # used to statically check permission definition
        self.permissions_in_scopes: Dict[str, Set[str]] = {}

        # populate roles strategies
        for scope in self.system_scopes.scopes:
            if scope.name not in indexed_strategies:
                raise ValueError(f'No role retrieval strategy defined for scope "{scope}"')

            self.roles_retrieval_strategies[scope.name] = indexed_strategies[scope.name]

        # populate permission sets
        for scope in self.system_scopes.scopes:
            scope_perms = set()
            for role in scope.roles:
                scope_perms.update(role.permissions)
            self.permissions_in_scopes[scope.name] = scope_perms

    def is_permission_in_scope(self, *, scope_name: str, permission: str) -> bool:
        """ Check if scope with ``scope_name`` has the ``permission`` assigned to any of its roles. """
        return permission in self.permissions_in_scopes[scope_name]

    def get_scope_retrieval_strategy(self, scope_name: str) -> callable:
        """ Retrieve scope with ``scope_name`` roles retrieval strategy. """
        if scope_name not in self.roles_retrieval_strategies:
            raise ValueError(f'Retrieval strategy not available for scope "{scope_name}"')

        return self.roles_retrieval_strategies[scope_name]

    def has_permission(self, *, scope_name: str, permission: str, subject_roles: List[str]) -> bool:
        """
        Check if any of the given roles have a specific permission within a scope.
            :param scope: The name of the scope in which to check the permission.

        :type scope: str
        :param permission: The permission to check for.
        :type permission: str
        :param subject_roles: A list of role names to check against the scope.
        :type subject_roles: List[str]
        :return: ``True`` if any role has the permission in the given scope, else ``False``.
        :rtype: bool
        """
        if (scope := self.system_scopes.get_scope(scope_name)) is None:
            raise ValueError(f'Scope does not exist "{scope_name}"')

        for role in subject_roles:
            if permission in scope.get_role_permissions(role):
                return True
        return False

    def has_priority(self, *, scope_name: str, subject_roles: List[str], target_roles: List[str]):
        """
        Determine if any subject role has higher priority than any target role within a given scope.

        :param scope_name: The name of the scope in which to evaluate role priority.
        :type scope_name: str
        :param subject_roles: A list of role names representing the subject.
        :type subject_roles: List[str]
        :param target_roles: A list of role names representing the target.
        :type target_roles: List[str]
        :return: ``True`` if any subject role has higher priority than any target role; otherwise ``False``.
        :rtype: bool
        """
        if (scope := self.system_scopes.get_scope(scope_name)) is None:
            raise ValueError(f'Scope does not exist "{scope_name}"')

        for s_role in subject_roles:
            for t_role in target_roles:
                s_role = scope.get_role(s_role)
                t_role = scope.get_role(t_role)
                if s_role is None or t_role is None:
                    continue
                if s_role > t_role:
                    return True
        return False

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
            return cls(SystemScopes(**yaml.safe_load(f)))
