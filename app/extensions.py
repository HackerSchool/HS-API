from flask_session import Session

session = Session()

from sqlalchemy import Engine, event
from sqlalchemy.orm import declarative_base  # noqa: E402

from flask_sqlalchemy import SQLAlchemy  # noqa: E402

db = SQLAlchemy(model_class=declarative_base())

# https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#foreign-key-support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

from flask_migrate import Migrate  # noqa: E402

migrate = Migrate()

