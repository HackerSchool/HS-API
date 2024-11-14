from typing import List, Tuple, Set

import json

from flask import Flask

# NOTE:
# The highest level is 0. So a role with level 1 is lower than a role with level 0.
# Likewise, a role with level 1 is consider higher than a role with level 2. 

class RolesHandler:
    def __init__(self):
        self.roles: dict[str: Tuple[int, Set[str]]] = None # indexes level and permissions set by role name
    
    def _get_role_level(self, role: str) -> int:
        """ Returns level of given role or 99 if role does not exist. """
        return self.roles.get(role, (99, None))[0]
    
    def _get_role_permissions(self, role: str) -> Set[str]:
        """ Returns set of role permissions or an empty set if role does not exist. """
        return self.roles.get(role, (None, set()))[1]

    def _get_highest(self, roles_list: list) -> Tuple[str, int]:
        """ Returns highest role and level in `roles_list` """
        highest_lvl = 99 
        highest_role = ""
        for role in roles_list:
            tag_lvl = self._get_role_level(role)
            if tag_lvl < highest_lvl:
                highest_lvl = tag_lvl 
                highest_role = role

        return highest_role, highest_lvl
 
    def exists_role(self, role):
        return role in self.roles.keys()

    def has_permission(self, roles_list: List[str], permission: str):
        """ Checks wether any role in `roles_list` has `permission`"""
        for role in roles_list:
            if permission in self._get_role_permissions(role):
                return True
        return False

    def has_higher_level(self, roles_list: List[str], role: str):
        """" Checks whether any role in `roles_list` has higher level than `role`. """
        _, highest_lvl = self._get_highest(roles_list)
        if highest_lvl == 0:
            return True # level 0 has all permissions
        return highest_lvl < self._get_role_level(role) # < instead of <= means we cannot add "horizontally"
    
    def init_app(self, app: Flask) -> None:
        # get configuration
        file_path = app.config.get("ROLES_PATH", "")
        if file_path == "":
            app.logger.error("ROLES_PATH environment not set")
            raise KeyError

        # load roles
        jsonData: any 
        try:
            with open(file_path, 'r') as f:
                jsonData = json.load(f)
        except FileNotFoundError:
            app.logger.error(f"Roles file {file_path} not found")
            raise
        except Exception:
            app.logger.error(f"Failed reading roles from file {file_path}")
            raise

        roles = jsonData.get("roles", "")
        if roles == "":
            app.logger.error(f"Missing 'roles' key")
            raise KeyError('roles')

        if not isinstance(roles, list):
            app.logger.error(f"Invalid 'roles' key value, expected list got {type(roles)}")
            raise ValueError('roles key')

        app.logger.info("Detecting roles:")
        # validate roles
        rolesDict = {}
        for role in roles:
            if not isinstance(role, dict):
                raise ValueError(f"Invalid role entry type, expected JSON object got {type(role)}")

            name = role.get("name", "")
            if name == "":
                raise KeyError("Missing 'name' key in role entry")
            if not isinstance(name, str):
                raise ValueError(f"Invalid 'name' key value type, expected string got {type(name)}")

            permissions = role.get("permissions", "")
            if permissions == "":
                raise KeyError("Missing 'permissions' key in role entry")
            if not isinstance(permissions, list):
                raise ValueError(f"Invalid 'permissions' key value type, expected list got {type(permissions)}")
            
            level = role.get("level", "")
            if level  == "":
                raise KeyError("Missing 'level' key in role entry")
            if not isinstance(level, int):
                raise ValueError(f"Invalid 'level' key value type, expected int got {type(level)}")
            
            app.logger.info(f"* {role['name']}")
            rolesDict[name] = (level, set(permissions))

        self.roles = rolesDict
        
 