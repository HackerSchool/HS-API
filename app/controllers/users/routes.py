from http import HTTPStatus

import jsonschema
from flask import abort, request, send_file, session

from app.controllers.decorators import requires_login, requires_permission
from app.controllers.users import bp
from app.services.roles import roles_service
from app.services.logos import logos_service
from app.services.logos.exceptions import (
    InvalidContentTypeError,
    InvalidLogoTypeError,
    LogoNotFoundError,
    LogoServiceException,
)

# from app.services.roles import roles_service
from app.services.users import user_service


@bp.route("", methods=["GET"])
@requires_login
@requires_permission(general=["read user"])
def get_users():
    """Returns all the user in the database in a list of JSON user objects."""
    return [m.to_dict() for m in user_service.get_all_users()]


@bp.route("", methods=["POST"])
@requires_login
@requires_permission(general=["create user"])
def create_member():
    """
    Creates a user member in the database with the information provided in the request body.
    Only users with the permission to create a user can create a member.
    An error is returned if the required fields are not provided.
    """
    mandatory_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string"},
            "ist_id": {"type": "string"},
            "name": {"type": "string"},
            "email": {"type": "string"},
            "course": {"type": "string"},
            "member_number": {"type": "number"},
            "join_date": {"type": "string"},
            "exit_date": {"type": "string"},
            "extra": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": [
            "username",
            "password",
            "ist_id",
            "name",
            "email",
            "course",
            "member_number",
            "join_date",
        ],
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, mandatory_schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    if user_service.get_user_by_ist_id(json_data["ist_id"]) is not None:
        abort(HTTPStatus.CONFLICT, description=f"User with IST ID '{json_data["ist_id"]}' already exists")

    if user_service.get_user_by_username(json_data["username"]) is not None:
        abort(HTTPStatus.CONFLICT, description=f"User '{json_data["username"]}' already exists")

    return user_service.create_member(**json_data).to_dict()


@bp.route("/<string:username>", methods=["GET"])
@requires_login
@requires_permission(general=["read user"])
def get_user_by_username(username):
    """
    Given a username, returns the JSON user object.
    An error is returned if the user does not exist.
    """
    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    return user.to_dict()


@bp.route("/<string:username>", methods=["PUT"])
@requires_login
@requires_permission(general=["edit user"], allow_self_action=True)
def update_user(username):
    """
    Edits the information of a user with the username provided.
    An error is returned if the user does not exist or the required fields are not provided.
    """
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "username": {"type": "string"},
            "course": {"type": "string"},
            "email": {"type": "string"},
            "description": {"type": "string"},
        },
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    updated_user = user_service.edit_user(user=user, **json_data)
    if session.get("username", "") != updated_user.username:
        session["username"] = updated_user.username

    return updated_user.to_dict()


@bp.route("/<string:username>", methods=["DELETE"])
@requires_login
@requires_permission(general=["delete user"], allow_self_action=True)
def delete_user(username):
    """
    Deletes user with provided username.
    Only users with the permission to delete a user can perform this action.
    An error is returned if the user does not exist.
    """
    member = user_service.get_user_by_username(username)
    if member is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User {username} not found")

    username = user_service.delete_user(member)

    if username == session.get("username", ""):
        session.clear()  # logout member if they deleted

    return {"message": "User deleted successfully!", "username": username}


@bp.route("/<string:username>/edit_password", methods=["PUT"])
@requires_login
@requires_permission(general=["edit password"], allow_self_action=True)
def edit_user_password(username):
    schema = {
        "type": "object",
        "properties": {
            "password": {"type": "string"},
        },
        "required": ["password"],
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    return user_service.edit_user_password(user, **json_data).to_dict()


################################################################################
############################### Participations #################################
################################################################################
@bp.route("/<string:username>/projects", methods=["GET"])
@requires_login
@requires_permission(general=["read user"], allow_self_action=True)
def get_user_projects(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    return [p.to_dict() for p in user.participations]


################################################################################
##################################### Roles ####################################
################################################################################
@bp.route("/<string:username>/roles", methods=["GET"])
@requires_login
@requires_permission(general=["read user"], allow_self_action=True)
def get_roles(username):
    """Get roles of a user."""
    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    return user.roles


@bp.route("/<string:username>/roles", methods=["PUT"])
@requires_login
@requires_permission(general=["edit role"])
def add_user_role(username):
    """Add role to a user."""
    mandatory_schema = {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
        },
        "required": ["role"],
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, mandatory_schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    role = json_data["role"]
    if not roles_service.exists_role_in_scope(scope="general", role=role):
        abort(HTTPStatus.BAD_REQUEST, description=f"Role '{role}' doesn't exist in 'general' scope")

    user_roles = session.get("roles", [])
    if not roles_service.has_higher_level(scope="general", roles=user_roles, role=role):
        abort(HTTPStatus.UNAUTHORIZED, description="You don't have permission to add that role")

    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    roles = user_service.add_user_role(user, **json_data)
    if roles is None:
        abort(HTTPStatus.BAD_REQUEST, description=f"User '{username}' already has this role")

    if session.get("username", "") == user.username:
        session["roles"] = roles

    return roles


@bp.route("/<string:username>/roles", methods=["DELETE"])
@requires_login
@requires_permission(general=["edit role"])
def remove_user_role(username):
    """Remove role from a member."""
    mandatory_schema = {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
        },
        "required": ["role"],
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, mandatory_schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    role = json_data["role"]
    if not roles_service.exists_role_in_scope(scope="general", role=role):
        abort(HTTPStatus.BAD_REQUEST, description=f"Role '{role}' doesn't exist in 'general' scope")

    user_roles = session.get("roles", [])
    if not roles_service.has_higher_level(scope="general", roles=user_roles, role=role):
        abort(HTTPStatus.UNAUTHORIZED, description="You don't have permission to add that role")

    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    roles = user_service.remove_user_role(user, **json_data)
    if roles is None:
        abort(HTTPStatus.BAD_REQUEST, description=f"User '{username}' does not have this role")

    if session.get("username", "") == user.username:
        session["roles"] = roles

    return roles


################################################################################
##################################### Logos ####################################
################################################################################
@bp.route("/<string:username>/logo", methods=["GET"])
@requires_login
@requires_permission(general=["read user"])
def get_user_logo(username):
    """Retrieve logo of a user given its' username"""
    if user_service.get_user_by_username(username) is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    try:
        logo_path, mimetype = logos_service.get_logo(username, logo_type="user")
    except LogoNotFoundError:
        abort(HTTPStatus.NOT_FOUND, description=f"Logo not found for user '{username}'")
    except InvalidLogoTypeError:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed saving logo to filesystem")

    return send_file(path_or_file=logo_path, mimetype=mimetype)


@bp.route("/<string:username>/logo", methods=["POST"])
@requires_login
@requires_permission(general=["edit user"], allow_self_action=True)
def set_member_logo(username):
    """Set the logo of a user given its' username"""
    if "file" not in request.files or request.files["file"] == "":
        abort(HTTPStatus.BAD_REQUEST, description="Missing file")

    file = request.files["file"]
    if file.content_type is None:
        abort(HTTPStatus.BAD_REQUEST, description="Missing file content type")

    if user_service.get_user_by_username(username) is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    try:
        logos_service.save_logo(username, file, logo_type="user")
    except InvalidContentTypeError as e:
        abort(HTTPStatus.BAD_REQUEST, description=f"Invalid image content-type {e.content_type}")
    except InvalidLogoTypeError:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Internal server error")
    except LogoServiceException:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed saving logo to filesystem")

    return {"message": "Logo uploaded sucessfully"}
