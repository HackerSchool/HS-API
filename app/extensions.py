from flask_session import Session
session = Session()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
db = SQLAlchemy(model_class=declarative_base())

from app.tags.tags_handler import TagsHandler
from app.logos.logos_handler import LogosHandler
tags_handler = TagsHandler() 
logos_handler = LogosHandler() 

