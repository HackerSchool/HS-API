import secrets
import time
from flask import request, jsonify, session, Blueprint
from functools import wraps

# Session token expiration time
SESSION_EXPIRATION_TIME = 600  # 10 minutes
# Dictionary to store session keys with expiration times
user_sessions = {}

# Helper function to check if a session key is valid
def is_session_valid(username, session_key):
    if username in user_sessions:
        stored_key, expiration_time = user_sessions[username]
        if stored_key == session_key and time.time() < expiration_time:
            return True
    return False

# Helper function to require login and session key
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        session_key = session.get('session_key')

        if not username or not session_key or not is_session_valid(username, session_key):
            return jsonify({"message": "Unauthenticated access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

def createAuthBlueprint(login_manager, session_expiration_seconds: int = SESSION_EXPIRATION_TIME):
    auth_bp = Blueprint('auth', __name__)

    # Route to log in users
    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Check if username exists and password is correct
            # This call returns hte list of tags a user has in the format: 'tag1,tag2,...'
        login = login_manager.login(username, password)
        if login:
            # Generate a unique session key and expiration time (e.g., 1 hour)
            session_key = secrets.token_hex(16)
            expiration_time = time.time() + session_expiration_seconds  # 1 hour from now

            # Store the session key and expiration time
            user_sessions[username] = (session_key, expiration_time)

            # Save session key and username in Flask session
            session['username'] = username
            session['session_key'] = session_key
            session['tags'] = login

            return jsonify({"message": f"Welcome {username}!", "session_key": session_key})
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    # Route to log out users
    @auth_bp.route('/logout')
    def logout():
        username = session.pop('username', None)
        session.pop('session_key', None)
        session.pop('tags', None)

        if username in user_sessions:
            user_sessions.pop(username)

        return jsonify({"message": "Logged out successfully"})

    return auth_bp
