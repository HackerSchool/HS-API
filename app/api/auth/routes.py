from flask import request, jsonify, session
from http import HTTPStatus

from app.api.auth import bp
from app.api.extensions import login_manager

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # This call returns the list of tags a user has in the format: 'tag1,tag2,...'
    if (tags := login_manager.login(username, password)) is None:
        return jsonify({"error": "Invalid credentials"}), HTTPStatus.UNAUTHORIZED

    # Save session key and username in Flask session
    session.clear()
    session['username'] = username
    session['tags'] = tags
    return jsonify({"message": f"Welcome {username}!"}), HTTPStatus.OK

    # Route to log out users
@bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), HTTPStatus.OK

