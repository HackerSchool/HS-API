import bcrypt


import secrets
from urllib.parse import urlencode
from jsonschema import validate, ValidationError

from flask import request, jsonify, session, current_app, redirect, abort
from http import HTTPStatus

from app.controllers.auth import bp
from app.controllers.decorators import requires_login

from app.services.users import user_service
from app.services.fenix import fenix_service


@bp.route("/login", methods=["POST"])
def login():
    mandatory_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
        },
        "required": ["username", "password"],
        "additionalProperties": False,
    }

    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    user = user_service.get_user_by_username(json_data.get("username"))
    if user is None:
        abort(HTTPStatus.UNAUTHORIZED, description="Invalid credentials")

    if not bcrypt.checkpw(
        json_data.get("password").encode("utf-8"), user.password.encode("utf-8")
    ):
        abort(HTTPStatus.UNAUTHORIZED, description="Invalid credentials")

    session.clear()
    session["username"] = user.username
    session["roles"] = user.roles
    return jsonify({"message": f"Welcome {user.username}!"})


@bp.route("/logout")
@requires_login
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@bp.route("/fenix-auth")
def fenix_auth():
    if fenix_service.is_not_implemented():
        abort(HTTPStatus.NOT_IMPLEMENTED, description="Unsupported")

    state = secrets.token_hex(16)

    session.clear()
    session["state"] = state
    params = {
        "client_id": fenix_service.client_id(),
        "redirect_uri": fenix_service.redirect_url(),
        "state": state,
    }
    return redirect(
        "https://fenix.tecnico.ulisboa.pt/oauth/userdialog?" + urlencode(params)
    )


@bp.route("/fenix-auth-callback")
def fenix_auth_callback():
    if request.args.get("state", "") != session.get("state", "_"):
        abort(HTTPStatus.UNAUTHORIZED, description="Unauthorized")

    if (err := request.args.get("error", "")) != "":
        abort(HTTPStatus.UNAUTHORIZED, description=f"Failed completing OAuth Flow with Fenix: {err}")

    if (code := request.args.get("code", "")) == "":
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed completing OAuth Flow with Fenix")

    access_token = fenix_service.exchange_access_token(code)
    if access_token is None:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed obtaining access token from Fenix.")

    success, ist_id, name, email = fenix_service.get_user_info(access_token)
    if not success:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed obtaining user information from Fenix")

    session.clear()
    member = user_service.get_member_by_ist_id(ist_id)
    if member is None:
        # redirect to register
        session["ist_id"] = ist_id
        session["name"] = name
        redirect_uri = (
            current_app.config.get("FRONTEND_URI")
            + "/regiser?"
            + urlencode({"ist_id": ist_id, "name": name, "email": email})
        )
        return redirect(redirect_uri)

    session["username"] = member.username
    session["roles"] = member.roles
    return redirect(current_app.config.get("FRONTEND_URI"))


@bp.route("/register", methods=["POST"])
def register():
    if session.get("ist_id", "") == "" or session.get("name", "") == "":
        abort(HTTPStatus.UNAUTHORIZED, description="Unauthorized")

    mandatory_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
            "ist_id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "course": {"type": "string"},
        },
        "required": ["username", "password", "ist_id", "name", "email", "course"],
        "additionalProperties": False,
    }

    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    if (session.get("ist_id", "") != json_data.get("ist_id", "_")) or (
        session.get("name", "") != json_data.get("name", "_")
    ):
        abort(HTTPStatus.BAD_REQUEST, description="'ist_id' or 'name' doesn't match Fenix credentials")

    applicant = user_service.create_applicant(**json_data)
    # login the user after registration
    session.clear()
    session["roles"] = applicant.roles
    session["username"] = applicant.username
    return applicant.to_dict()
