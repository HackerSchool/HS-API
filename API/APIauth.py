from flask import request, jsonify, session, Blueprint
from functools import wraps

# Helper function to check if a user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"message": "Unauthorized access, please log in"}), 403
        return f(*args, **kwargs)
    return decorated_function

def createAuthBlueprint(login_manager):
    auth_bp = Blueprint('auth', __name__)

    # Route to log in users
    @auth_bp.route('/login', methods=['POST'])
    def login():
        data = request.json
        username = data.get('username')
        password = data.get('password')

        # Check if username exists and password is correct
        login = login_manager.login(username, password)
        if login:
            session['username'] = username
            return jsonify({"message": f"Welcome {username}!"})
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    # Route to log out users
    @auth_bp.route('/logout')
    def logout():
        session.pop('username', None)
        return jsonify({"message": "Logged out successfully"})
    
    return auth_bp