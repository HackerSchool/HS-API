import secrets

from http import HTTPStatus

from flask import Blueprint
from flask import abort
from flask import redirect

from flask import request
from flask import session

from app.auth.fenix.fenix_service import FenixService
from app.repositories.member_repository import MemberRepository
from app.auth.auth_controller import AuthController

from app.schemas.login_schema import LoginSchema
from app.schemas.member_schema import MemberSchema
from app.schemas.fenix_callback_schema import FenixCallbackSchema
from app.schemas.fenix_user_schema import FenixUserSchema

from app.auth.utils import current_member


def create_login_bp(*, member_repo: MemberRepository, auth_controller: AuthController, fenix_service: FenixService):
    bp = Blueprint("auth", __name__)

    @bp.route("/login", methods=["POST"])
    @auth_controller.login_member
    def login():
        login_data = LoginSchema(**request.json)
        if (member := member_repo.get_member_by_username(login_data.username)) is None:
            return None
        if member.password is None:  # fenix authenticated users must login through Fenix
            return None
        if not member.matches_password(login_data.password):
            return None
        return member

    @bp.route("/logout", methods=["GET"])
    @auth_controller.logout_member
    def logout():
        return {"message": "Logout successful!", "username": current_member.username}

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

        state = secrets.token_hex(16)
        session.clear()
        session["state"] = state
        return redirect(fenix_service.redirect_url(state=state))

    @bp.route(fenix_service.redirect_endpoint)
    @auth_controller.login_member
    def fenix_auth_callback():
        callback_args = FenixCallbackSchema(**request.args)
        if "state" not in session and callback_args.state != session["state"]:
            return abort(HTTPStatus.UNAUTHORIZED)
        if callback_args.error:
            return abort(HTTPStatus.BAD_GATEWAY, description=callback_args.error)

        token = fenix_service.fetch_access_token(redirect_endpoint="/fenix-login-callback", code=callback_args.code)
        fenix_user_schema = FenixUserSchema(**fenix_service.fetch_user_info(token))
        if (member := member_repo.get_member_by_ist_id(fenix_user_schema.ist_id)) is None:
            return abort(HTTPStatus.UNAUTHORIZED)
        return member

    return bp
