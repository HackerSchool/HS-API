import bcrypt

from typing import List

from jsonschema import validate, ValidationError

from flask import request, jsonify, session
from http import HTTPStatus

from app.api.auth import bp
from app.api.decorators import requires_login

from app.api.errors import throw_api_error

from app.services import member_service

@bp.route('/login', methods=['POST'])
def login():
    mandatory_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ["username", "password"],
        "additionalProperties": False
    }

    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})

    member = member_service.get_member_by_username(json_data.get("username"))
    if member is None:
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Invalid credentials"})

    if not bcrypt.checkpw(json_data.get("password").encode('utf-8'), member.password.encode('utf-8')):
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Invalid credentials"})

    session.clear()
    session['username'] = member.username
    session['tags'] = member.tags
    return jsonify({"message": f"Welcome {member.username}!"})

@bp.route('/logout')
@requires_login
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

