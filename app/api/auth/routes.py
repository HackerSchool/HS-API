from typing import List

from flask import request, jsonify, session
from http import HTTPStatus

from app.api.auth import bp
from app.api.decorators import login_required

from app.api.errors import throw_api_error

from app.services import login_service
from app.services.login_service import exceptions as login_exceptions

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    # This call returns the list of tags a user has in the format: 'tag1,tag2,...'
    tags : List[str] 
    try:
        tags = login_service.login(username, password)
    except login_exceptions.AuthError as e:
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Invalid credentials"})

    # Save session key and username in Flask session
    session.clear()
    session['username'] = username
    session['tags'] = tags 
    return jsonify({"message": f"Welcome {username}!"}), HTTPStatus.OK

@bp.route('/logout')
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), HTTPStatus.OK

