import secrets
import time
from flask import request, jsonify, session, Blueprint
from functools import wraps

# Helper function to require login, checks if the session has expired
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        if not username:
            return jsonify({"message": "Unauthenticated access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

def createAuthBlueprint(login_manager):
    auth_bp = Blueprint('auth', __name__)

    # Route to log in users
    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        # TODO: Implement encryption
        # This data should arrive encrypted to the system, so that a man in the middle attack is not possible
        # on the login request to the server
        username = data.get('username')
        password = data.get('password')

        # Check if username exists and password is correct
            # This call returns hte list of tags a user has in the format: 'tag1,tag2,...'
        login = login_manager.login(username, password)
        if login:
            # Save session key and username in Flask session
            session['username'] = username
            session['tags'] = login
            session.permanent = True

            return jsonify({"message": f"Welcome {username}!"})
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    # Route to log out users
    @auth_bp.route('/logout')
    def logout():
        username = session.pop('username', None)
        session.pop('tags', None)

        if username in user_sessions:
            user_sessions.pop(username)

        return jsonify({"message": "Logged out successfully"})

    return auth_bp
