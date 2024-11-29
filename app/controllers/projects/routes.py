from http import HTTPStatus

import jsonschema
from flask import abort, jsonify, request, send_file

from app.controllers.decorators import requires_login, requires_permission
from app.controllers.projects import bp
from app.services.logos import logos_service
from app.services.logos.exceptions import (
    InvalidContentTypeError,
    InvalidLogoTypeError,
    LogoNotFoundError,
    LogoServiceException,
)
from app.services.projects import project_service
from app.services.users import user_service


@bp.route("", methods=["GET"])
@requires_login
@requires_permission(general=["read project"])
def get_projects():
    """Returns a list of all projects in a list of json project objects"""
    return [p.to_dict() for p in project_service.get_all_projects()]


@bp.route("", methods=["POST"])
@requires_login
@requires_permission(general=["create project"])
def create_project():
    """
    Creates a project in the database with the information provided in the request body.
    Only users with the permission to create a project can create a project.
    An error is returned if the required fields are not provided.
    """
    mandatory_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "start_date": {"type": "string"},
            "state": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["name", "start_date", "state"],
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, mandatory_schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    if project_service.get_project_by_name(json_data["name"]) is not None:
        abort(HTTPStatus.CONFLICT, description=f"Project '{json_data['name']}' already exists")

    return project_service.create_project(**json_data).to_dict()


@bp.route("/<string:project_name>", methods=["GET"])
@requires_login
@requires_permission(general=["read project"])
def get_project_by_name(project_name):
    """
    Given a project name, returns the JSON project object.
    An error is returned if the project does not exist
    """
    project = project_service.get_project_by_name(project_name)
    if project is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    return project.to_dict()


@bp.route("/<string:project_name>", methods=["PUT"])
@requires_login
@requires_permission(general=["edit project"], project=["edit project"])
def update_project(project_name):
    """
    Edits the information of a project with the name provided.
    An error is returned if the member does not exist or the required fields are not provided.
    """
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "number"},
            "start_date": {"type": "string"},
            "state": {"type": "string"},
            "description": {"type": "string"},
        },
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    project = project_service.get_project_by_name(name=project_name)
    if project is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    return project_service.edit_project(name=project_name, **json_data).to_dict()


@bp.route("/<string:project_name>", methods=["DELETE"])
@requires_login
@requires_permission(general=["delete project"])
def delete_project(project_name):
    """
    Deletes a member with provided name.
    An error is returned if the project does not exist.
    """
    project = project_service.get_project_by_name(name=project_name)
    if project is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    p_name = project_service.delete_project(project)
    return jsonify({"message": "Project deleted successfully!", "name": p_name})


################################################################################
############################### Project Members ################################
################################################################################
@bp.route("/<string:project_name>/users", methods=["GET"])
@requires_login
@requires_permission(general=["read project"])
def get_project_users(project_name):
    project = project_service.get_project_by_name(project_name)
    if project is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    return [p.to_dict() for p in project.participations]


@bp.route("/<string:project_name>/<string:username>", methods=["POST"])
@requires_login
@requires_permission(general=["edit project"], project=["add participant"])
def add_user_to_project(project_name, username):
    mandatory_schema = {
        "type": "object",
        "properties": {
            "entry_date": {"type": "string"},
            "contributions": {"type": "number"},
        },
        "required": ["entry_date"],
        "additionalProperties": False,
    }
    json_data = request.json
    try:
        jsonschema.validate(json_data, mandatory_schema)
    except jsonschema.ValidationError as e:
        abort(HTTPStatus.BAD_REQUEST, description=e.message)

    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    project = project_service.get_project_by_name(project_name)
    if project is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    participation = project_service.add_user_to_project(user, project, **json_data)
    if participation is None:
        abort(HTTPStatus.BAD_REQUEST, description="User is already associated with the project")

    return {"message": "User added to project", **participation.to_dict()}


@bp.route("/<string:project_name>/<string:username>", methods=["DELETE"])
@requires_login
@requires_permission(general=["edit project"], project=["remove participant"])
def delete_user_from_project(project_name, username):
    user = user_service.get_user_by_username(username)
    if user is None:
        abort(HTTPStatus.NOT_FOUND, description=f"User '{username}' not found")

    project = project_service.get_project_by_name(project_name)
    if project is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    participation = project_service.remove_user_from_project(user, project)
    if participation is None:
        abort(HTTPStatus.BAD_REQUEST, description="User is not associated with the project")

    return {
        "message": "User removed from project",
        "username": participation.member_username,
        "project": participation.project_name,
    }


###############################################################################
################################### Logos #####################################
###############################################################################
@bp.route("/<string:project_name>/logo", methods=["GET"])
@requires_login
@requires_permission(general=["read project"])
def get_project_logo(project_name):
    """Retrieve logo of a project given its' ID"""
    if project_service.get_project_by_name(project_name) is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    try:
        logo_path, mimetype = logos_service.get_logo(project_name, logo_type="project")
    except LogoNotFoundError:
        abort(HTTPStatus.NOT_FOUND, description=f"Logo not found for project '{project_name}'")
    except InvalidLogoTypeError:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed saving logo to filesystem")

    return send_file(path_or_file=logo_path, mimetype=mimetype)


@bp.route("/<string:project_name>/logo", methods=["POST"])
@requires_login
@requires_permission(general=["edit project"], project=["update logo"])
def set_project_logo(project_name):
    """Set the logo of a project given its' name"""
    if "file" not in request.files or request.files["file"] == "":
        abort(HTTPStatus.BAD_REQUEST, description="Missing file")

    file = request.files["file"]
    if file.content_type is None:
        abort(HTTPStatus.BAD_REQUEST, description="Missing file content type")

    if project_service.get_project_by_name(project_name) is None:
        abort(HTTPStatus.NOT_FOUND, description=f"Project '{project_name}' not found")

    try:
        logos_service.save_logo(project_name, file, logo_type="project")
    except InvalidContentTypeError as e:
        abort(HTTPStatus.BAD_REQUEST, description=f"Invalid image content-type {e.content_type}")
    except InvalidLogoTypeError:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Internal server error")
    except LogoServiceException:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, description="Failed saving logo to filesystem")

    return jsonify({"message": "Logo uploaded successfully"})
