from flask import Flask
from flask_session import Session
import os

from datetime import timedelta
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

def _get_env_or_default(env: str, default: str, cast=None):
    val = os.environ.get(env, "")
    if not val:
        return default

    return cast(val) if cast is not None else val


class Config:
    SECRET_KEY = _get_env_or_default("SECRET_KEY", secrets.token_hex(256))
    SESSION_TYPE = _get_env_or_default("SESSION_TYPE", 'filesystem')  # Store session data in the filesystem
    SESSION_FILE_DIR = _get_env_or_default("SESSION_DIR", os.path.join(os.getcwd(), 'data/flask_session'))  # Directory to store session files
    SESSION_PERMANENT = _get_env_or_default("SESSION_PERMANENT", True, lambda x : x.lower == "true")        # Whether to use permanent sessions
    SESSION_USE_SIGNER = _get_env_or_default("SESSION_USE_SIGNER", True, lambda x : x.lower == "true")      # Whether to sign the session ID cookie for security
    SESSION_KEY_PREFIX = _get_env_or_default("SESSION_KEY_PREFIX", 'my_session_')  # Prefix for session files
    session_expiration = 30
    try:
        session_expiration = _get_env_or_default("PERMANENTE_SESSION_LIFETIME", 30, int)
    except ValueError:
        pass
    PERMANENT_SESSION_LIFETIME = session_expiration 
 
    DATABASE_PATH = _get_env_or_default("DATABASE_PATH", 'data/hackerschool.sqlite3')
    TAGS_PATH = _get_env_or_default("TAGS_PATH", 'data/tags.json')
    LOGOS_PATH = _get_env_or_default("LOGOS_PATH", 'data/logos/')
