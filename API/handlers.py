from databaseHandling import member, member_project, project

class Handlers:
    def __init__(self, db_handler):
        self.memberHandler = member.MemberHandler(db_handler)
        self.projectHandler = project.ProjectHandler(db_handler)
        self.memberProjectHandler = member_project.MemberProjectHandler(db_handler)