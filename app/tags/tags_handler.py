import json

from flask import Flask

_PERMISSIONS_ERR_MESSAGES = {
    "create_member": "You don't have permission to create members",
    "delete_member": "You don't have permission to delete members",
    "edit_member": "You don't have permission to edit members",
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
                allTagNames = self.tags.keys()
                print("Detecting tags:")
                for tag in self.tags:
                    print(" * "+tag)
                file.close()
        except FileNotFoundError:
            print("File not found")
            return None
        
    def canSingle(self, tag: str, request: str):
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
    
    def can(self, tag_list: list, request: str, tagToAdd: str = None):
        # can = False
        # Can we modify this tag? If it has an higher level than our highest tag, return False
        if tagToAdd is not None:
            # Check if the tagToAdd exists
            if tagToAdd not in self.tags:
                print(f"Tag {tagToAdd} not found")
                return False
            targetTag_value = self.tags[tagToAdd]["level"]
            myHieghest = self.tags[self.getHighiest(tag_list)]["level"]
            if myHieghest < targetTag_value:
                return False
            else:
                return True

        for tag in tag_list:
            if self.canSingle(tag, request):
                return True
                # can = True
                # break
        # return can
        return False
    
    def getHighiest(self, tags_list: list):
        highiest = 10000
        highiest_tag = ""
        for tag in tags_list:
            if tag not in self.tags:
                continue
            if self.tags[tag]["level"] < highiest:
                highiest = self.tags[tag]["level"]
                highiest_tag = tag
        if highiest_tag == "":
            return None
        return highiest_tag