import os
import secrets

from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__)) + "/.." # the repository folder 

load_dotenv(basedir + ".env")

def _get_env_or_default(env: str, default: str, cast=None):
    val = os.environ.get(env, "")
    if not val:
        return default

    return cast(val) if cast is not None else val

class Config:
    SECRET_KEY =         _get_env_or_default("SECRET_KEY", secrets.token_hex(256))
    SESSION_TYPE =       _get_env_or_default("SESSION_TYPE", 'filesystem') # Store session data in the filesystem
    SESSION_PERMANENT =  _get_env_or_default("SESSION_PERMANENT", True, lambda x : x.lower == "true")  # Whether to use permanent sessions
    SESSION_USE_SIGNER = _get_env_or_default("SESSION_USE_SIGNER", True, lambda x : x.lower == "true") # Whether to sign the session ID cookie for security
    SESSION_KEY_PREFIX = _get_env_or_default("SESSION_KEY_PREFIX", 'my_session_') # Prefix for session files
    session_expiration = 30
    try:
        session_expiration = _get_env_or_default("PERMANENTE_SESSION_LIFETIME", 30, int)
    except ValueError:
        pass
    PERMANENT_SESSION_LIFETIME = session_expiration 
 
    SESSION_FILE_DIR = os.path.join(basedir, _get_env_or_default("SESSION_DIR",   'data/flask_session')).rstrip("/")
    DATABASE_PATH    = os.path.join(basedir, _get_env_or_default("DATABASE_PATH", 'data/hackerschool.sqlite3')).rstrip("/")
    TAGS_PATH        = os.path.join(basedir, _get_env_or_default("TAGS_PATH",     'data/tags.json')).rstrip("/")
    LOGOS_PATH       = os.path.join(basedir, _get_env_or_default("LOGOS_PATH",    'data/logos/')).rstrip("/")

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH