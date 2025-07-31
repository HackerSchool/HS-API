from http import HTTPStatus

from flask import Blueprint, request, abort

from app.repositories.member_repository import MemberRepository
from app.access.access_controller import AccessController

from app.schemas.login_schema import LoginSchema
from app.schemas.member_schema import MemberSchema

from app.access.utils import current_member


def create_auth_bp(*, member_repo: MemberRepository, access_controller: AccessController):
    bp = Blueprint("auth", __name__)

    @bp.route("/login", methods=["POST"])
    @access_controller.login_member
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
    @access_controller.logout_member
    def logout():
        return {"message": "Logout successful!", "username": current_member.username}

    @bp.route("/me", methods=["GET"])
    @access_controller.requires_login
    def me():
        if access_controller.enabled:
            return MemberSchema.from_member(current_member).model_dump()
        else:
            return abort(HTTPStatus.NOT_FOUND)

    return bp

#     @bp.route("/fenix-auth")
#     def fenix_auth():
#         if (
#             current_app.config.get("CLIENT_ID", "") == ""
#             or current_app.config.get("CLIENT_SECRET", "") == ""
#             or current_app.config.get("FENIX_REDIRECT_URL") == ""
#         ):
#             abort(HTTPStatus.NOT_IMPLEMENTED)
#
#         state = secrets.token_hex(16)
#
#         session.clear()
#         session["state"] = state
#         params = {
#             "client_id": current_app.config.get("CLIENT_ID"),
#             "redirect_uri": current_app.config.get("FENIX_REDIRECT_URL"),
#             "state": state,
#         }
#         return redirect(
#             "https://fenix.tecnico.ulisboa.pt/oauth/userdialog?" + urlencode(params)
#         )
#
#     @bp.route("/fenix-auth-callback")
#     def fenix_auth_callback():
#         try:
#             oauth_data = FenixOAuthSchema(**request.args)
#         except ValidationError:
#             # this fails on invalid state parameters
#             abort(HTTPStatus.UNAUTHORIZED)
#
#         if oauth_data.state is None or oauth_data.state != session.get("state", ""):
#             abort(HTTPStatus.UNAUTHORIZED)
#
#         if oauth_data.error is not None:
#             abort(HTTPStatus.BAD_GATEWAY, {"error": oauth_data.error})
#
#         params = {
#             "client_id": current_app.config.get("CLIENT_ID"),
#             "client_secret": current_app.config.get("CLIENT_SECRET"),
#             "redirect_uri": current_app.config.get("FENIX_REDIRECT_URL"),
#             "code": oauth_data.code,
#             "grant_type": "authorization_code",
#         }
#
#         if (
#             access_token := __fetch_access_token(
#                 "https://fenix.tecnico.ulisboa.pt/oauth/access_token?"
#                 + urlencode(params)
#             )
#         ) is None:
#             abort(HTTPStatus.BAD_GATEWAY)
#
#         if (user_data := __get_user_info(access_token)) is None:
#             abort(HTTPStatus.BAD_GATEWAY)
#
#         session.clear()
#         if (member := member_repo.get_member_by_ist_id(user_data.username)) is None:
#             # attempt to create a user with a random username
#             while True:
#                 while True:
#                     # generate a random username
#                     username = base62.encodebytes(random.randbytes(8)).lower()
#                     if member_repo.get_member_by_username(username) is None:
#                         break
#
#                 try:
#                     pass
#                     # member = member_service.create_user(Member(MemberSchema(**user_data)))
#                 except Exception as e:
#                     print(e)
#                     # TODO replace with conflict exception
#                     continue
#                 break
#
#         session["username"] = member.username
#         return {"message": "Registered"}
#
#     return bp
#
#
# def __fetch_access_token(url: str) -> str | None:
#     r = requests.post(url)
#     try:
#         r.raise_for_status()
#     except requests.HTTPError as e:
#         current_app.logger.info(f"Failed requesting access token: {e}")
#         return None
#
#     if r.status_code != 200:
#         current_app.logger.info(
#             f"Failed requesting access token with non 200 response. Status code: {r.status_code}\nMessage: {r.connection}"
#         )
#         return None
#
#     access_token: str
#     try:
#         access_token = r.json()["access_token"]
#     except Exception as e:
#         current_app.logger.info(f"Failed requesting access token: {e}")
#         return None
#
#     return access_token
#
#
# def __get_user_info(
#     access_token: str,
# ) -> FenixStudentSchema | None:
#     r = requests.get(
#         "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person?"
#         + urlencode({"access_token": access_token})
#     )
#     try:
#         r.raise_for_status()
#     except requests.HTTPError as e:
#         current_app.logger.info(f"Failed requesting user info: {e}")
#         return None
#
#     if r.status_code != 200:
#         current_app.logger.info(
#             f"Failed requesting user info with non 200 status code. Status Code: {r.status_code}\nMessage: {r.content}"
#         )
#         return None
#
#     try:
#         user_data = FenixStudentSchema(**r.json())
#     except Exception as e:
#         current_app.logger.info(f"Failed requesting user info: {e}")
#         return None
#
#     return user_data
