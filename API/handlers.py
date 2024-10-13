from databaseHandling import member, member_project, project, images_handler

class Handlers:
    def __init__(self, db_handler, images_folder: str = "."):
        self.memberHandler = member.MemberHandler(db_handler)
        self.projectHandler = project.ProjectHandler(db_handler)
        self.memberProjectHandler = member_project.MemberProjectHandler(db_handler)
        self.logosHandler = images_handler.Logos(images_folder)