import json

class Tags:
    def __init__(self, tagsFilename: str):
        self.tags = None
        self.tagsFilename = tagsFilename

        # Recieves a tags.json file, with a field called tags, which is a list of tags
        # Example of a Tag:
        # "member": {
        #     "name": "Member",
        #     "description": "The person who is a member of the company.",
        #     "color": "#FFFFFF",
        #     "level": 4,
        #     "permissions": {
        #         "create_member": false,
        #         "delete_member": false,
        #         "create_delete": false,
        #         "delete_delete": false
        #     }
        # }
        try:
            with open(tagsFilename, "r") as file:
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
        can = False

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
                can = True
                break
        return can
    
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


if __name__ == "__main__":
    tags = Tags("tags.json")
    print(tags.can("sysadmin", "create_member"))