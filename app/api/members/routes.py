from jsonschema import validate, ValidationError

from flask import jsonify, request, session
from http import HTTPStatus

from app.extensions import roles_handler

from app.services import member_service, project_service, member_project_service

from app.api.members import bp
from app.api.errors import throw_api_error
from app.api.decorators import requires_login, requires_permission 

@bp.route('', methods=['GET'])
@requires_login
@requires_permission('read member')
def get_members():
    """ Returns all the members in the database in a list of JSON member objects. """
    return [m.to_dict() for m in member_service.get_all_members()]

@bp.route('', methods=['POST'])
@requires_login
@requires_permission('create member')
def create_member():
    """
    Creates a member in the database with the information provided in the request body.
    Only users with the permission to create a member can create a member.
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
        "required": ["username", "password", "ist_id", "name", "email", "course", "member_number", "join_date"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})

    return member_service.create_member(**json_data).to_dict()

@bp.route('/<string:username>', methods=['GET'])
@requires_login
@requires_permission('read member', allow_self_action=True)
def get_member(username):
    """
    Given a member username, returns the JSON member object.
    An error is returned if the member does not exist.
    """
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    return member.to_dict()

@bp.route('/<string:username>', methods=['PUT'])
@requires_login
@requires_permission('edit member', allow_self_action=True)
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
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": "Missing data in body"})
    try:
        validate(json_data, schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
    
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    return member_service.edit_member(member=member, **json_data).to_dict()
 
@bp.route('/<string:username>', methods=['DELETE'])
@requires_login
@requires_permission('delete member', allow_self_action=True)
def delete_member(username):
    """
    Deletes a member with provided username.
    Only users with the permission to delete a member can delete a member.
    An error is returned if the member does not exist.
    """
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    m_id = member_service.delete_member(member)

    if member.username == session.get("username", ""):
        session.clear() # logout member if it deleted itself

    return jsonify({"message": "Member deleted successfully!", "member_id": m_id})

@bp.route('/<string:username>/edit_password', methods=['PUT'])
@requires_login
@requires_permission('edit member', 'edit password', allow_self_action=True)
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

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    return member_service.edit_member_password(member, **json_data).to_dict()


################################################################################
############################### Member Projects ################################
################################################################################

@bp.route('/<string:username>/projects', methods=['GET'])
@requires_login
@requires_permission('read member', allow_self_action=True)
def get_member_projects(username):
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    return [p.to_dict() for p in member_project_service.get_member_projects(member)]

@bp.route('/<string:username>/<string:proj_name>', methods=['POST'])
@requires_login
@requires_permission('edit project')
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

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    project = project_service.get_project_by_name(proj_name)
    if project is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Project not found"})
    
    return member_project_service.create_member_project(member, project, **json_data).to_dict()

@bp.route('/<string:username>/<string:proj_name>', methods=['DELETE'])
@requires_login
@requires_permission('edit project')
def delete_member_project(username, proj_name):
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
    
    p_id = member_project_service.delete_member_project(member, proj_name)
    if p_id is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member is not associated with the project"})

    return jsonify({"message": "Member not longer associated with project", "project_id": p_id})


################################################################################
##################################### Roles ####################################
################################################################################

@bp.route('/<string:username>/roles', methods=['GET'])
@requires_login
@requires_permission('read member')
def get_member_roles(username):
    """
    Given a member username, returns the roles associated with the member
    In case the member does not exist, a 404 error is returned
    """
    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})
    
    return {"roles": member.roles}

@bp.route('/<string:username>/roles', methods=['PUT'])
@requires_login
@requires_permission('edit member')
def add_member_role(username): 
    """
    Adds role to a member.
    An error is returned if the member does not exist, the role is already associated with the member or the user does not have permission
    You cannot add a role with an higher permission level than your own.
    """       
    mandatory_schema = {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
        },
        "required": ["role"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
    
    # Does the user have permission to add a role to the member?
    user_roles = session.get('roles', [])
    if not roles_handler.has_higher_level(user_roles, role=json_data["role"]):
        throw_api_error(HTTPStatus.FORBIDDEN, {"error": "You don't have permission to add that role"})

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    roles = member_service.add_member_role(member, **json_data)
    if roles is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "User already has this role"})
    
    if session.get('username', '') == member.username:
        session['roles'] = roles

    return roles

@bp.route('/<string:username>/roles', methods=['DELETE'])
@requires_login
@requires_permission('edit member')
def remove_member_role(username):
    """
    Attempts to remove a role from a member.
    Only users with the permission to remove a role can remove a role.
    An error is returned if the member does not exist, the role is not associated with the member or the user does not have permission
    """
    mandatory_schema = {
        "type": "object",
        "properties": {
            "role": {"type": "string"},
        },
        "required": ["role"],
        "additionalProperties": False
    }
    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})

    # Does the user have permission to remove a role from the member?
    user_roles = session.get('roles', [])
    if not roles_handler.has_higher_level(user_roles, role=json_data["role"]):
        throw_api_error(HTTPStatus.FORBIDDEN, {"error": "You don't have permission to remove that tag"})

    member = member_service.get_member_by_username(username)
    if member is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "Member does not exist"})

    roles = member_service.remove_member_role(member, **json_data)
    if roles is None:
        throw_api_error(HTTPStatus.NOT_FOUND, {"error": "User does not have this role"})

    if session.get('username', '') == member.username:
        session['roles'] = roles

    return roles

@bp.route('/register', methods=['POST'])
def register():
    if session.get("ist_id", "") == "" or session.get("name", "") == "":
        throw_api_error(HTTPStatus.UNAUTHORIZED, {"error": "Unauthorized"})

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
        "additionalProperties": False
    }

    json_data = request.json
    try:
        validate(json_data, mandatory_schema)
    except ValidationError as e:
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": e.message})
    
    if session.get("ist_id", "") != json_data.get("ist_id", "_") or \
        session.get("name", "") != json_data.get("name", "_"):
        throw_api_error(HTTPStatus.BAD_REQUEST, {"error": "ist_id or name doesn't match Fenix credentials"})
    
    new_member = member_service.create_applicant(**json_data)
    # login the user after registration
    session.clear()
    session['roles'] = new_member.roles
    session['username'] = new_member.username
    return new_member.to_dict()
