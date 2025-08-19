import os
import secrets
from datetime import timedelta
from typing import List

from cachelib import FileSystemCache
from dotenv import load_dotenv
from redis import Redis

basedir = os.path.abspath(
    os.path.abspath(os.path.dirname(__file__)) + "/.."
)  # the repositories folder

load_dotenv(os.path.join(basedir, ".env"))


def _get_env_or_default(env: str, default: str, cast=None):
    if (val := os.environ.get(env, None)) is None:
        return default
    return cast(val) if cast is not None else val


def _get_int_env_or_default(env: str, default: str) -> int:
    try:
        return _get_env_or_default(env, default, int)
    except ValueError:
        return default


def _get_bool_env_or_false(env: str) -> bool:
    return os.environ.get(env, False) in ['True', 'true', 1]


class Config:
    SECRET_KEY = secrets.token_hex()

    MAX_CONTENT_LENGTH: int = 16 * 1000 * 1000 # max for file uplaods

    # see https://flask-session.readthedocs.io/en/latest/config.html#
    SESSION_TYPE: str = _get_env_or_default("SESSION_TYPE", "cachelib")
    if SESSION_TYPE == "cachelib":
        SESSION_CACHELIB = FileSystemCache(
            cache_dir=os.path.join(basedir, _get_env_or_default("SESSION_DIR", "resources/flask_sessions")),
            threshold=500,
        )
    elif SESSION_TYPE == "redis":
        SESSION_REDIS = Redis.from_url(url=_get_env_or_default("SESSION_REDIS", ""))

    PERMANENT_SESSION_LIFETIME = _get_int_env_or_default("PERMANENT_SESSION_LIFETIME", timedelta(days=14))

    SQLALCHEMY_DATABASE_URI: str = ("sqlite:///" + os.path.join(basedir, _get_env_or_default("SQLALCHEMY_DATABASE_URI", "resources/hackerschool.sqlite3")))

    ROLES_PATH:  str = os.path.join(basedir, _get_env_or_default("ROLES_PATH", "resources/roles.yaml"))
    IMAGES_PATH: str = os.path.join(basedir, _get_env_or_default("IMAGES_PATH", "resources/images/"))

    ROOT_URI = _get_env_or_default("ROOT_URI", "http://localhost:5000")

    ENABLED_ACCESS_CONTROL: bool = _get_bool_env_or_false("ENABLED_ACCESS_CONTROL")
    ORIGINS_WHITELIST: List = _get_env_or_default("ORIGINS_WHITELIST", "http://localhost:5173").split()

    CLIENT_ID:     str =           _get_env_or_default("CLIENT_ID", "")
    CLIENT_SECRET: str =           _get_env_or_default("CLIENT_SECRET", "")
    FENIX_REDIRECT_ENDPOINT: str = _get_env_or_default("FENIX_REDIRECT_ENDPOINT", "/fenix-login-callback")

    SESSION_COOKIE_SAMESITE = _get_env_or_default("SAME_SITE_POLICY", "Strict")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE   = True

    SENTRY_DSN: str = _get_env_or_default("SENTRY_DSN", "")
