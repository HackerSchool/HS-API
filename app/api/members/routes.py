from typing import List
from jsonschema import validate, ValidationError

from flask import jsonify, request, session
from http import HTTPStatus

from app.api.errors import throw_api_error

from app.services import member_service, project_service, member_project_service

from app.api.members import bp
from app.api.decorators import login_required, required_permission
from app.extensions import tags_handler

@bp.route('', methods=['GET'])
# @login_required
def get_members():
    """ Returns all the members in the database in a list of JSON member objects. """
    return [m.to_dict() for m in member_service.get_all_members()]

@bp.route('', methods=['POST'])
# @login_required
# @required_permission("create_member")
def create_member():
    """
    Creates a member in the database with the information provided in the request body.
    Only users with the permission to create a member can create a member.
    An error is returned if the required fields are not provided.
    """
    mandatory_schema = {
        "type": "object",
        "properties": {
            "ist_id": {"type": "string"},
            "member_number": {"type": "number"},
            "name": {"type": "string"},
            "username": {"type": "string"},
            "password": {"type": "string"},
            "join_date": {"type": "string"},
            "course": {"type": "string"},
            "email": {"type": "string"},
            "exit_date": {"type": "string"},
            "extra": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["ist_id", "member_number", "name", "username", "password", "join_date", "course", "email"],
        "additionalProperties": False
    }
    # Validate request 
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
        # return jsonify({"error": e.message}), HTTPStatus.BAD_REQUEST

    return member_service.create_member(**json_data).to_dict()

@bp.route('/<string:username>', methods=['GET'])
# @login_required
def get_member(username):
    """
    Given a member username, returns the JSON member object.
    An error is returned if the member does not exist.
    """
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "Member does not exist"}), HTTPStatus.NOT_FOUND

    return member.to_dict()

@bp.route('/<string:username>', methods=['PUT'])
# @login_required
# @required_permission('edit_member', allow_self_action=True)
def update_member(username):
    """
    Edits the information of a member with the username provided.
    An error is returned if the member does not exist or the required fields are not provided.
    """
    schema = {
        "type": "object",
        "properties": {
            "ist_id": {"type": "string"},
            "member_number": {"type": "number"},
            "name": {"type": "string"},
            "join_date": {"type": "string"},
            "course": {"type": "string"},
            "email": {"type": "string"},
            "exit_date": {"type": "string"},
            "extra": {"type": "string"},
            "description": {"type": "string"},
        },
        "additionalProperties": False
    }
    json_data = request.json
    if json_data is None:
        # return jsonify({'error': 'No data provided for update'}), HTTPStatus.BAD_REQUEST
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": "Missing data in body"})
    try:
        validate(json_data, schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
        # return jsonify({"error": e.message}), HTTPStatus.BAD_REQUEST
    
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "Member does not exist"}), HTTPStatus.NOT_FOUND

    return member_service.edit_member(member=member, **json_data).to_dict()
 
@bp.route('/<string:username>', methods=['DELETE'])
# @login_required
# @required_permission('delete_member', allow_self_action=True)
def delete_member(username):
    """
    Deletes a member with provided username.
    Only users with the permission to delete a member can delete a member.
    An error is returned if the member does not exist.
    """
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "Member does not exist"}), HTTPStatus.NOT_FOUND

    m_id = member_service.delete_member(member)
    return jsonify({"message": "Member deleted successfully!", "member_id": m_id})

@bp.route('/<string:username>/edit_password', methods=['PUT'])
def edit_password(username):
    schema = {
        "type": "object",
        "properties": {
            "password": {"type": "string"},
        },
        "required": ["password"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
        # return jsonify({"error": e.message}), HTTPStatus.BAD_REQUEST

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "Member does not exist"}), HTTPStatus.NOT_FOUND

    return member_service.edit_member(member, **json_data) 

################################################################################
############################### Member Projects ################################
################################################################################
@bp.route('/<string:username>/projects', methods=['GET'])
def get_member_projects(username):
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "User doesn't exist"}), HTTPStatus.NOT_FOUND 

    return member_project_service.get_member_projects(member)

# @login_required
@bp.route('/<string:username>/<string:proj_name>', methods=['POST'])
def add_member_project(username, proj_name):
    mandatory_schema = {
        "type": "object",
        "properties": {
            "entry_date": {"type": "string"},
            "contributions": {"type": "number"},
        },
        "required": ["entry_date"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
        # return jsonify({"error": e.message}), HTTPStatus.BAD_REQUEST

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "User does not exist"}), HTTPStatus.NOT_FOUND 

    project = project_service.get_project_by_name(proj_name)
    if project is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Project not found"})
        # return jsonify({"error": "Project not found"}), HTTPStatus.NOT_FOUND 
    
    return member_project_service.create_member_project(member, project, **json_data)

@bp.route('/<string:username>/<string:proj_name>', methods=['DELETE'])
def delete_member_project(username, proj_name):
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({"error": "User does not exist"}), HTTPStatus.NOT_FOUND 
    
    p_id = member_project_service.remove_member_project(member, proj_name)
    if p_id is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "User is not associated with the project"})

    return jsonify({"message": "Member not longer associated with project", "project_id": p_id})

################################################################################
##################################### Tags #####################################
################################################################################
@bp.route('/<string:username>/tags', methods=['GET'])
# @login_required
def get_member_tags(username):
    """
    Given a member username, returns the tags associated with the member
    In case the member does not exist, a 404 error is returned
    """
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
    
    # if only one tag, don't split string
    tags: List[str] = [member.tags,] if "," not in member.tags else member.tags.split(",")
    return {"tags": tags}

@bp.route('/<string:username>/tags', methods=['PUT'])
# @login_required
def add_member_tag(username): 
    """
    Attempt to add a tag to a member
    Only users with the permission to add a tag can add a tag
    An error is returned if the member does not exist, the tag is already associated with the member or the user does not have permission
    You cannot add a tag with an highier permission level than your own
    """       
    mandatory_schema = {
        "type": "object",
        "properties": {
            "tag": {"type": "string"},
        },
        "required": ["tag"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
    
    # Does the user have permission to add a tag to the member?
    # user_tags = session['tags'].split(',')
    # if not tags_handler.can(user_tags, 'add_tag', tag_to_add=json_data['tag']):
    #     return jsonify({'message': 'You do not have permission to add that tag'}), HTTPStatus.FORBIDDEN

    # Get the member ID from the username
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({'error': 'Member does not found'}), HTTPStatus.NOT_FOUND

    return member_service.add_member_tag(member, **json_data)

@bp.route('/<string:username>/tags', methods=['DELETE'])
# @login_required
def remove_member_tag(username):
    """
    Attempts to remove a tag from a member.
    Only users with the permission to remove a tag can remove a tag.
    An error is returned if the member does not exist, the tag is not associated with the member or the user does not have permission
    """
    mandatory_schema = {
        "type": "object",
        "properties": {
            "tag": {"type": "string"},
        },
        "required": ["tag"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
        # return jsonify({"error": e.message}), HTTPStatus.BAD_REQUEST
    # Get the request data

    # Does the user have permission to remove a tag from the member?
    # user_tags = session.get('tags').split(',')
    # if not tags_handler.can(user_tags, 'add_tag', tag_to_add=json_data['tag']):
    #     return jsonify({'error': 'You do not have permission to remove that tag'}), HTTPStatus.FORBIDDEN

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
        # return jsonify({'error': 'Member not found'}), HTTPStatus.NOT_FOUND 

    tags = member_service.remove_member_tag(username, **json_data)
    if tags is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "User does not have this tag"})
        # return jsonify({"error": "User does not have this tag"}), HTTPStatus.NOT_FOUND

    return member_service.remove_member_tag(username, **json_data)
