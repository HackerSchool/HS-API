from typing import List, Tuple

import json

from flask import Flask

_PERMISSIONS_ERR_MESSAGES = {
    "read_member": "You don't have permission to read members",
    "create_member": "You don't have permission to create members",
    "delete_member": "You don't have permission to delete members",
    "edit_member": "You don't have permission to edit members",
    "read_project": "You don't have permission to read projects",
    "create_project": "You don't have permission to create projects",
    "delete_project": "You don't have permission to delete projects",
    "edit_project": "You don't have permission to edit projects",
    "edit_password": "You don't have permission to edit passwords",
}

class TagsHandler:
    def __init__(self):
        self.tags = None
    
    @staticmethod
    def get_permission_err_message(tag: str) -> str:
        return _PERMISSIONS_ERR_MESSAGES.get(tag)
   
    def init_app(self, app: Flask) -> None:
        try:
            with open(app.config["TAGS_PATH"], "r") as file:
                self.tags = json.load(file)["tags"]
                print("Detecting tags:")
                for tag in self.tags:
                    print(" * "+tag)
                file.close()
        except FileNotFoundError:
            print("File not found")
            return None
        
    def can(self, tag_list: List[str], permission: str, tag_to_add: str = None):
        """" 
        Check whether `tag_list` can execute `permission`. 
        If `tag_to_add` is provided, checks whether `tag_list` highest is higher than `tag_to_add`.
        """
        if tag_to_add is None:
            for tag in tag_list:
                if self._can_single(tag, permission):
                    return True

        if tag_to_add not in self.tags:
            return False

        _, highest_lvl = self._get_highest(tag_list)
        if highest_lvl == 0: # 0 is the highest level with all permission 
            return True

        if highest_lvl < self._get_tag_level(tag_to_add): # < instead of <= means we cannot add "horizontally"
            return True 

        return False 
    
    def _get_tag_level(self, tag: str) -> int:
        """ Returns level of given tag or 99 if tag does not exist. """
        return self.tags.get(tag, {}).get("level", 99)

    def _get_highest(self, tags_list: list) -> Tuple[str, int]:
        """ Returns highest tag and level in `tags_list` """
        highest_lvl = 99 
        highest_tag = ""
        for tag in tags_list:
            tag_lvl = self._get_tag_level(tag)
            if tag_lvl < highest_lvl:
                highest_lvl = tag_lvl 
                highest_tag = tag

        return highest_tag, highest_lvl

    def _can_single(self, tag: str, permission: str):
        """ Check whether `tag` can execute `permission` """
        if tag not in self.tags: # tag doesn't exist
            return False
        if permission not in self.tags[tag]["permissions"]: # permission doesn't exist in tag
            return False

        return self.tags[tag]["permissions"][permission]
    
 
