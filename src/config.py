from flask import Flask
from flask_session import Session
import os

from datetime import timedelta
import secrets

basedir = os.path.abspath(os.path.dirname(__file__))

SESSION_EXPIRATION_TIME = 30
class Config:
    SECRET_KEY = secrets.token_hex(256)
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=SESSION_EXPIRATION_TIME)

    # Configure server-side session storage to use the filesystem
    SESSION_TYPE = 'filesystem'  # Store session data in the filesystem
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'flask_session')  # Directory to store session files
    SESSION_PERMANENT = True  # Whether to use permanent sessions
    SESSION_USE_SIGNER = True  # Whether to sign the session ID cookie for security
    SESSION_KEY_PREFIX = 'my_session_'  # Prefix for session files
    DATABASE_PATH = 'hackerschool.db'
    TAGS_PATH = 'tags.json'
    LOGOS_PATH = 'logos/'
