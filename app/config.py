import os

from datetime import timedelta
from dotenv import load_dotenv
from redis import Redis
from cachelib import FileSystemCache

basedir = os.path.abspath(
    os.path.abspath(os.path.dirname(__file__)) + "/.."
)  # the repositories folder

load_dotenv(os.path.join(basedir, ".env"))


def _get_env_or_default(env: str, default: str, cast=None):
    val = os.environ.get(env, "")
    if not val:
        return default

    return cast(val) if cast is not None else val


def _get_int_env_or_default(env: str, default: str) -> int:
    try:
        return _get_env_or_default(env, default, int)
    except ValueError:
        return default


class Config:
    # see https://flask-session.readthedocs.io/en/latest/config.html#
    SESSION_TYPE = _get_env_or_default("SESSION_TYPE", "cachelib")
    if SESSION_TYPE == "cachelib":
        SESSION_CACHELIB = FileSystemCache(
            cache_dir=os.path.join(
                basedir, _get_env_or_default("SESSION_DIR", "resources/")
            ),
            threshold=500,
        )
    elif SESSION_TYPE == "redis":
        SESSION_REDIS = Redis.from_url(url=_get_env_or_default("SESSION_REDIS", ""))

    PERMANENT_SESSION_LIFETIME = _get_int_env_or_default(
        "PERMANENT_SESSION_LIFETIME", timedelta(days=14)
    )

    DATABASE_PATH = os.path.join(
        basedir, _get_env_or_default("DATABASE_PATH", "resources/hackerschool.sqlite3")
    )
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_PATH

    ROLES_PATH = os.path.join(
        basedir, _get_env_or_default("ROLES_PATH", "resources/roles.yaml")
    )

    STATIC_DIR = os.path.join(
        basedir, _get_env_or_default("STATIC_DIR", "resources/static/")
    ).rstrip("/")
    MAX_CONTENT_LENGTH = _get_int_env_or_default(
        "MAX_FILE_UPLOAD_LENGTH", 16 * 1024 * 1024
    )

    LOGS_PATH = os.path.join(basedir, _get_env_or_default("LOGS_PATH", ""))

    FRONTEND_URI = _get_env_or_default("FRONTEND_URI", "http://localhost:3000")

    ENABLED_ACCESS_CONTROL = _get_env_or_default("ENABLED_ACCESS_CONTROL", False)

    CLIENT_ID = _get_env_or_default("CLIENT_ID", "")
    CLIENT_SECRET = _get_env_or_default("CLIENT_SECRET", "")
    FENIX_REDIRECT_URL = _get_env_or_default("FENIX_REDIRECT_URL", "")
