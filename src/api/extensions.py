from database.database_handler import DatabaseHandler
from tags.tags_handler import TagsHandler
from logos.logos_handler import LogosHandler

from services.login_manager import LoginManager
from services.member import MemberHandler
from services.project import ProjectHandler
from services.member_project import MemberProjectHandler

db_handler = DatabaseHandler()
tags_handler = TagsHandler() 
logos_handler = LogosHandler() 

login_manager = LoginManager(db_handler)
project_service = ProjectHandler(db_handler)
member_service = MemberHandler(db_handler)
member_project_service = MemberProjectHandler(db_handler)