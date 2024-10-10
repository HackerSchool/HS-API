from flask import Flask
from flask_session import Session
import os

from databaseHandling import database_handler, login_manager
from API import APImembers, APIauth, APIprojects, handlers
from Tags import Tags
from datetime import timedelta
import secrets

# Time to live for the session
SESSION_EXPIRATION_TIME = 30  # 30 seconds - for testing

# Initializing Database and Login Manager
tags = Tags("tags.json")
db_handler = database_handler.DatabaseHandler('hackerschool.db')
lm = login_manager.LoginManager(db_handler)

handlers = handlers.Handlers(db_handler)

# Initializing Flask App and configuring
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=SESSION_EXPIRATION_TIME)
app.secret_key = secrets.token_hex(256)

# Configure server-side session storage to use the filesystem
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in the filesystem
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')  # Directory to store session files
app.config['SESSION_PERMANENT'] = True  # Whether to use permanent sessions
app.config['SESSION_USE_SIGNER'] = True  # Whether to sign the session ID cookie for security
app.config['SESSION_KEY_PREFIX'] = 'my_session_'  # Prefix for session files

# TODO : System to clean the session data after the sessions expires

Session(app)

# Registering Blueprints
############# Auth #############
    # Requires login_manager to be passed as an argument, so that we can validate the login
app.register_blueprint(APIauth.createAuthBlueprint(lm))
############# Members #############
    # Requires db_handler to be passed as an argument, so that we can interact with the database
    # Requires login_required to be passed as an argument, so that we can validate if the user is logged in
app.register_blueprint(APImembers.createMembersBlueprint(handlers, APIauth.login_required, tags))
############# Projects #############
    # Requires db_handler to be passed as an argument, so that we can interact with the database
    # Requires login_required to be passed as an argument, so that we can validate if the user is logged in
app.register_blueprint(APIprojects.createProjectBlueprint(handlers, APIauth.login_required, tags))


if __name__ == '__main__':
    app.run(debug=True, port=5100)