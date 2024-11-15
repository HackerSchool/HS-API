import bcrypt

from typing import List

from urllib.parse import urlencode
from jsonschema import validate, ValidationError

from flask import request, jsonify, session, current_app, redirect
from http import HTTPStatus

from app.api.auth import bp
from app.api.decorators import requires_login
from app.api.errors import throw_api_error

from app.services import member_service

from .utils import generate_random_state, fetch_access_token, get_user_ist_id

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
    session['roles'] = member.roles
    return jsonify({"message": f"Welcome {member.username}!"})

@bp.route('/logout')
@requires_login
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@bp.route('/fenix-auth')
def oauth():
    if current_app.config.get("CLIENT_ID", "") == "" \
        or current_app.config.get("CLIENT_SECRET", "") == "" \
            or current_app.config.get("OAUTH_CALLBACK") == "":
        throw_api_error(HTTPStatus.NOT_IMPLEMENTED, {"error": "Unsupported"})

    state = generate_random_state()

    session.clear()
    session['state'] = state
    params = {
        "client_id": current_app.config.get("CLIENT_ID"),
        "redirect_uri": current_app.config.get("OAUTH_CALLBACK"),
        "state": state
    }
    return redirect("https://fenix.tecnico.ulisboa.pt/oauth/userdialog?" + urlencode(params))

@bp.route('/fenix-auth-callback')
def oauth_callback():
    if request.args.get("state", "") != session.get("state", "_"):
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Unauthorized"})

    if (err := request.args.get("error", "")) != "":
        current_app.logger.info(f"Failed completing OAuth flow. {err}")
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Failed completing OAuth Flow with Fénix"})

    if (code := request.args.get("code", "")) == "":
        throw_api_error(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Failed completing OAuth Flow with Fénix"})
    
    params = {
        "client_id": current_app.config.get("CLIENT_ID"),
        "client_secret": current_app.config.get("CLIENT_SECRET"),
        "redirect_uri": current_app.config.get("OAUTH_CALLBACK"),
        "code": code,
        "grant_type": "authorization_code"
    }
    access_token = \
        fetch_access_token("https://fenix.tecnico.ulisboa.pt/oauth/access_token?" + urlencode(params))
    if access_token is None:
        throw_api_error(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Failed obtaining access token from Fénix."})
   
    ist_id = get_user_ist_id(access_token)
    if ist_id is None:
        throw_api_error(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "Failed obtaining user information from Fénix"})
    
    member = member_service.get_member_by_ist_id(ist_id)
    if member is None:
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Unauthorized"})

    session.clear()
    session['username'] = member.username
    session['roles'] = member.roles
    return redirect(current_app.config.get('FRONTEND_URI'))
