from app.database.database_handler import DatabaseHandler
from app.tags.tags_handler import TagsHandler
from app.logos.logos_handler import LogosHandler

from app.services.login_manager import LoginManager
from app.services.member import MemberHandler
from app.services.project import ProjectHandler
from app.services.member_project import MemberProjectHandler

db_handler = DatabaseHandler()
tags_handler = TagsHandler() 
logos_handler = LogosHandler() 

login_manager = LoginManager(db_handler)
project_service = ProjectHandler(db_handler)
member_service = MemberHandler(db_handler)
member_project_service = MemberProjectHandler(db_handler)