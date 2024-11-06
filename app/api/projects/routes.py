from jsonschema import validate, ValidationError
from http import HTTPStatus

from flask import request, jsonify

from app.services import project_service, member_project_service

from app.api.projects import bp
from app.api.errors import throw_api_error
from app.api.decorators import login_required, required_permission

@bp.route('', methods=['GET'])
@login_required
def get_projects():
    """ Returns a list of all projects in a list of json project objects """
    return [p.to_dict() for p in project_service.get_all_projects()]

@bp.route('', methods=['POST'])
@login_required
@required_permission('create_project')
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
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error((HTTPStatus.BAD_REQUEST, {"error": e.message}))

    return project_service.create_project(**json_data).to_dict()

@bp.route('/<string:name>', methods=['GET'])
@login_required
def get_project(name):
    """
    Given a project name, returns the JSON project object.
    An error is returned if the project does not exist
    """
    project = project_service.get_project_by_name(name)
    if not project:
        throw_api_error((HTTPStatus.NOT_FOUND, {"error": "Project not found"}))

    return project.to_dict()

@bp.route('/<string:name>', methods=['PUT'])
@login_required
@required_permission('edit_project')
def update_project(name):
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
        "additionalProperties": False
    }
    json_data = request.json
    if not json_data:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": "Missing data in body"})
    try:
        validate(json_data, schema)
    except ValidationError as e:
        throw_api_error((HTTPStatus.BAD_REQUEST, {"error": e.message}))
    
    project = project_service.edit_member_by_username(name=name, **json_data)
    if project is None:
        throw_api_error((HTTPStatus.NOT_FOUND, {"error": "Project not found"}))

    return project.to_dict()

@bp.route('/<string:name>', methods=['DELETE'])
@login_required
@required_permission('delete_project')
def delete_project(name):
    """
    Deletes a member with provided name.
    An error is returned if the project does not exist.
    """
    p_id = project_service.delete_project_by_name(name)
    if p_id is None:
        throw_api_error((HTTPStatus.NOT_FOUND, {"error": "Project not found"}))

    return jsonify({"message": "Project deleted successfully!", "id": p_id})


################################################################################
##################################### Project Members #####################################
################################################################################
@bp.route('/<string:name>/members', methods=['GET'])
@login_required
def get_project_members(name):
    project = project_service.get_project_by_name(name)
    if project is None:
        throw_api_error((HTTPStatus.NOT_FOUND, {"error": "Project not found"}))

    return member_project_service.get_project_members(project) 

@bp.route('/<string:name>/members', methods=['GET'])
def add_project_member(name):
    # TODO
    pass

@bp.route('/<string:name>/members', methods=['DELETE'])
def delete_project_member(name):
    # TODO
    pass

