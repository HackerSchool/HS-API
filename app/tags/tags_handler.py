import json

from flask import Flask

_PERMISSIONS_ERR_MESSAGES = {
    "create_member": "You don't have permission to create members",
    "delete_member": "You don't have permission to delete members",
    "edit_member": "You don't have permission to edit members",
    "edit_password": "You don't have permission to edit passwords",
    "edit_password": "You don't have permission to edit passwords",
    "create_project": "You don't have permission to create projects",
    "delete_project": "You don't have permission to delete projects",
    "edit_project": "You don't have permission to edit projects",
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
        
    def can_single(self, tag: str, request: str):
        # If the tag does not exist in the tags, return False
        if tag not in self.tags:
            print(f"Tag {tag} not found")
            return False
        if request not in self.tags[tag]["permissions"]:
            print(f"Request \"{request}\" not found in tag {tag}")
            return False
        if tag in self.tags:
            return self.tags[tag]["permissions"][request]
        return False
    
    def can(self, tag_list: list, request: str, tag_to_add: str = None):
        # Can we modify this tag? If it has an higher level than our highest tag, return False
        if tag_to_add is not None:
            # Check if the tagToAdd exists
            if tag_to_add not in self.tags:
                print(f"Tag {tag_to_add} not found")
                return False
            target_tag_value = self.tags[tag_to_add]["level"]
            my_highest = self.tags[self.get_highest(tag_list)]["level"]
            if my_highest < target_tag_value:
                return False
            else:
                return True

        for tag in tag_list:
            if self.can_single(tag, request):
                return True

        return False
    
    def get_highest(self, tags_list: list):
        highest = 10000
        highest_tag = ""
        for tag in tags_list:
            if tag not in self.tags:
                continue
            if self.tags[tag]["level"] < highest:
                highest = self.tags[tag]["level"]
                highest_tag = tag
        if highest_tag == "":
            return None
        return highest_tag