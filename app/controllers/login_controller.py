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
        # Temporarily disable origin validation for testing
        # if origin not in current_app.config["ORIGINS_WHITELIST"]:
        #     return abort(HTTPStatus.BAD_REQUEST, f"Origin '{origin}' is not whitelisted ")

        state = secrets.token_hex(16)
        session.clear()
        session["state"] = state
        session["next"] = next_param
        session.permanent = True  # Mark session as permanent
        
        # Build root_uri from current request to ensure callback goes to the same server
        # This fixes the issue where ROOT_URI is set to production but user is in development
        # Check for X-Forwarded-Proto header (common in reverse proxies) to get correct scheme
        original_scheme = request.headers.get('X-Forwarded-Proto', request.scheme)
        scheme = original_scheme
        # Force https for production domains (hackerleague.app)
        if '.hackerleague.app' in request.host or request.host == 'api.hackerleague.app':
            scheme = 'https'
        request_root_uri = f"{scheme}://{request.host}"
        session["root_uri"] = request_root_uri  # Store in session for callback
        
        # Debug: Log session creation
        print(f"[DEBUG] Fenix login - Request scheme (original): {original_scheme}")
        print(f"[DEBUG] Fenix login - Request scheme (final): {scheme}")
        print(f"[DEBUG] Fenix login - Request host: {request.host}")
        print(f"[DEBUG] Fenix login - X-Forwarded-Proto header: {request.headers.get('X-Forwarded-Proto', 'NOT SET')}")
        print(f"[DEBUG] Fenix login - Created session with state: {state[:8]}..., next: {next_param}")
        print(f"[DEBUG] Fenix login - Request root_uri: {request_root_uri}")
        print(f"[DEBUG] Fenix login - Session keys: {list(session.keys())}")
        print(f"[DEBUG] Fenix login - Session cookie domain: {current_app.config.get('SESSION_COOKIE_DOMAIN')}")
        print(f"[DEBUG] Fenix login - Session cookie SameSite: {current_app.config.get('SESSION_COOKIE_SAMESITE')}")
        
        # Force session to be saved before redirect
        # This ensures the cookie is set and will be sent when Fenix redirects back
        try:
            session.modified = True
            # Access session to trigger save
            _ = session.get("state")
        except Exception as e:
            print(f"[DEBUG] Error saving session before redirect: {e}")
        
        fenix_url = fenix_service.redirect_url(state=state, root_uri=request_root_uri)
        # Extract redirect_uri from the generated URL for debugging
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(fenix_url)
        redirect_uri_in_url = parse_qs(parsed.query).get('redirect_uri', [None])[0]
        print(f"[DEBUG] Fenix login - Redirect URI being sent to Fenix: {redirect_uri_in_url}")
        print(f"[DEBUG] Fenix login - Redirecting to: {fenix_url}")
        return redirect(fenix_url)

    @bp.route(fenix_service.redirect_endpoint)
    @auth_controller.login_member
    def fenix_auth_callback():
        # Debug: Log session state
        print(f"[DEBUG] Callback - Session keys: {list(session.keys())}")
        print(f"[DEBUG] Callback - Session has 'next': {'next' in session}")
        print(f"[DEBUG] Callback - Session has 'state': {'state' in session}")
        print(f"[DEBUG] Callback - Session has 'root_uri': {'root_uri' in session}")
        print(f"[DEBUG] Callback - Request args: {dict(request.args)}")
        
        if "next" not in session:
            print(f"[DEBUG] Callback - ERROR: 'next' not in session. Session keys: {list(session.keys())}")
            return abort(HTTPStatus.UNAUTHORIZED, description="Session expired or invalid. Please try logging in again.")

        callback_args = FenixCallbackSchema(**request.args)
        if callback_args.error:
            return abort(HTTPStatus.BAD_GATEWAY, description=callback_args.error)

        if "state" not in session or callback_args.state != session["state"]:
            print(f"[DEBUG] Callback - State mismatch. Session state: {session.get('state')}, Callback state: {callback_args.state}")
            return None, session["next"]

        # Use root_uri from session (set during fenix-login) or fall back to configured one
        root_uri = session.get("root_uri", current_app.config["ROOT_URI"])
        # Ensure https for production domains
        if root_uri.startswith('http://') and ('.hackerleague.app' in root_uri or 'api.hackerleague.app' in root_uri):
            root_uri = root_uri.replace('http://', 'https://')
            session["root_uri"] = root_uri  # Update session with corrected URI
        print(f"[DEBUG] Callback - Using root_uri: {root_uri}")
        print(f"[DEBUG] Callback - Using redirect_endpoint: {fenix_service.redirect_endpoint}")
        full_redirect_uri = root_uri + fenix_service.redirect_endpoint
        print(f"[DEBUG] Callback - Full redirect_uri being sent to Fenix: {full_redirect_uri}")
        
        # Use the same redirect_endpoint that was used in redirect_url to ensure consistency
        token = fenix_service.fetch_access_token(redirect_endpoint=fenix_service.redirect_endpoint, code=callback_args.code, root_uri=root_uri)
        fenix_user_schema = FenixUserSchema(**fenix_service.fetch_user_info(token))
        if (member := member_repo.get_member_by_ist_id(fenix_user_schema.ist_id)) is None:
            print(f"[DEBUG] Callback - Member not found for IST ID: {fenix_user_schema.ist_id}")
            return None, session["next"]

        print(f"[DEBUG] Callback - Success! Member found: {member.username} (ID: {member.id})")
        return member, session["next"]

    return bp
