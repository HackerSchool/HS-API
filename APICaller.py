from flask import Flask

from databaseHandling import database_handler, login_manager
from API import APImembers, APIauth, APIprojects, handlers
from Tags import Tags
from datetime import timedelta

# Initializing Database and Login Manager
tags = Tags("file.tags")
db_handler = database_handler.DatabaseHandler('hackerschool.db')
lm = login_manager.LoginManager(db_handler)

handlers = handlers.Handlers(db_handler)

# Initializing Flask App and configuring
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)
app.secret_key = 'super secret key'

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