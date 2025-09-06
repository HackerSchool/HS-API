import secrets
from http import HTTPStatus
from urllib.parse import urlparse

from flask import Blueprint
from flask import abort
from flask import current_app
from flask import redirect
from flask import request
from flask import session

from app.auth.auth_controller import AuthController
from app.auth.fenix.fenix_service import FenixService
from app.auth.utils import current_member

from app.repositories.member_repository import MemberRepository

from app.schemas.fenix_callback_schema import FenixCallbackSchema
from app.schemas.fenix_user_schema import FenixUserSchema
from app.schemas.login_schema import LoginSchema
from app.schemas.member_schema import MemberSchema


def create_login_bp(*, member_repo: MemberRepository, auth_controller: AuthController, fenix_service: FenixService):
    bp = Blueprint("auth", __name__)

    @bp.route("/login", methods=["POST"])
    @auth_controller.login_member
    def login():
        login_data = LoginSchema(**request.json)
        if (member := member_repo.get_member_by_username(login_data.username)) is None:
            return None, None
        if member.password is None:  # fenix authenticated users must login through Fenix
            return None, None
        if not member.matches_password(login_data.password):
            return None, None
        return member, None

    @bp.route("/logout", methods=["GET"])
    @auth_controller.logout_member
    def logout():
        return {"description": "Logout successful!", "username": current_member.username}

    @bp.route("/me", methods=["GET"])
    @auth_controller.requires_login
    def me():
        if not auth_controller.enabled:
            return abort(HTTPStatus.NOT_FOUND)
        return MemberSchema.from_member(current_member).model_dump(exclude="password")

    @bp.route("/fenix-login")
    def fenix_login():
        if not auth_controller.enabled:
            return abort(HTTPStatus.NOT_IMPLEMENTED)

        if not (next_param := request.args.get("next", "")):
            return abort(HTTPStatus.BAD_REQUEST, 'Missing "next" query param')
        parsed_uri = urlparse(next_param)
        origin = parsed_uri.scheme + "://" + parsed_uri.netloc
        if origin not in current_app.config["ORIGINS_WHITELIST"]:
            return abort(HTTPStatus.BAD_REQUEST, f"Origin '{origin}' is not whitelisted ")

        state = secrets.token_hex(16)
        session.clear()
        session["state"] = state
        session["next"] = next_param
        return redirect(fenix_service.redirect_url(state=state))

    @bp.route(fenix_service.redirect_endpoint)
    @auth_controller.login_member
    def fenix_auth_callback():
        if "next" not in session:
            return abort(HTTPStatus.UNAUTHORIZED)

        callback_args = FenixCallbackSchema(**request.args)
        if callback_args.error:
            return abort(HTTPStatus.BAD_GATEWAY, description=callback_args.error)

        if "state" not in session or callback_args.state != session["state"]:
            return None, session["next"]

        token = fenix_service.fetch_access_token(redirect_endpoint="/fenix-login-callback", code=callback_args.code)
        fenix_user_schema = FenixUserSchema(**fenix_service.fetch_user_info(token))
        if (member := member_repo.get_member_by_ist_id(fenix_user_schema.ist_id)) is None:
            return None, session["next"]

        return member, session["next"]

    return bp
