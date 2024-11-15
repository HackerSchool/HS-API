from flask_session import Session
session = Session()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
db = SQLAlchemy(model_class=declarative_base())

from flask_migrate import Migrate
migrate = Migrate()

from app.roles.roles_handler import RolesHandler
roles_handler = RolesHandler() 

from app.logos.logos_handler import LogosHandler
logos_handler = LogosHandler() 

from app.commands.commands import *
