from flask import request, jsonify, session

from api.auth import bp
from api.extensions import login_manager

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Check if username exists and password is correct
    # This call returns hte list of tags a user has in the format: 'tag1,tag2,...'
    if tags := login_manager.login(username, password):
        # Save session key and username in Flask session
        session['username'] = username
        session['tags'] = tags
        session.permanent = True

        return jsonify({"message": f"Welcome {username}!"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

    # Route to log out users
@bp.route('/logout')
def logout():
    username = session.pop('username', None)
    session.pop('tags', None)

    return jsonify({"message": "Logged out successfully"})

