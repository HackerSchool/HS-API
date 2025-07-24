from flask_session import Session

session = Session()

from flask_sqlalchemy import SQLAlchemy  # noqa: E402
from sqlalchemy.orm import declarative_base  # noqa: E402

db = SQLAlchemy(model_class=declarative_base())

from flask_migrate import Migrate  # noqa: E402

migrate = Migrate()

