from flask import session, jsonify, request
from http import HTTPStatus

from app.api.members import bp
from app.api.decorators import login_required, required_permission
from app.api.extensions import member_service, member_project_service, tags_handler

@bp.route('', methods=['GET'])
@login_required
def get_members():
    """
    Returns all the members in the database in a list of lists,
    each list contains the information of a member

    The returned information is in the following format:
    [{
        "istID": "istID",
        "memberNumber": "memberNumber",
        "name": "name",
        "username": "username",
        "entry_date": "entry_date",
        "course": "course",
        "description": "description",
        "mail": "mail",
        "extra": "extra",
    }, ...]
    """
    members = member_service.listMembers()
    return jsonify(members), HTTPStatus.OK

@bp.route('', methods=['POST'])
@login_required
@required_permission('create_member')
def create_member():
    """
    Creates a member in the database with the information provided in the request
        Only users with the permission to create a member can create a member
        An error is returned if the required fields are not provided, the member already exists or the user does not have permission

        The format is the folowing:
        {
            "istID": "istID",
            "memberNumber": "memberNumber",
            "name": "name",
            "username": "username",
            "password": "password",
            "entry_date": "entry_date",
            "course": "course",
            "description": "description",
            "mail": "mail"
        }
        """
    # Validate request data
    data = request.json
    required_fields = ['istID', 'memberNumber', 'name', 'username', 'password', 'entry_date', 'course', 'description', 'mail']

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'message': 'Missing required fields', 'missing_fields': missing_fields}), HTTPStatus.BAD_REQUEST 

    # Proceed if all required fields are present
    ret = member_service.createMember(data['istID'], data['memberNumber'], data['name'], data['username'], 
                            data['password'], data['entry_date'], data['course'], 
                            data['description'], data['mail'], '{}', None, 'member')
    if not ret[0]:
        return jsonify({'message': ret[1]}), 400
    return jsonify({'message': 'Member created successfully!'})

@bp.route('/<string:username>', methods=['GET'])
@login_required
def get_member(username):
    """
    Given a member username, returns the information of the member
    In case the member does not exist, a 404 error is returned

    The returned information is in the following format:
    {
        "istID": "istID",
        "memberNumber": "memberNumber",
        "name": "name",
        "username": "username",
        "entry_date": "entry_date",
        "course": "course",
        "description": "description",
        "mail": "mail",
        "extra": "extra",
    }
    """
    member_data = member_service.getMemberInfo(username)
    # If the member does not exist
    if not member_data:
        return jsonify({'message': 'No member with that username!'}), HTTPStatus.NOT_FOUND
    return jsonify(member_data), HTTPStatus.OK

@bp.route('/<string:username>', methods=['PUT'])
@login_required
@required_permission('edit_member', allow_self_action=True)
def update_member(username):
    """
    Edits the information of a member with the username provided in the url
    Only users with the permission to edit a member can update a member
    An error is returned if the member does not exist, the user does not have permission or the data provided is invalid

    The format is the folowing:
    {
        "istID": "istID",
        "memberNumber": "memberNumber",
        "name": "name",
        "username": "username",
        "password": "password",
        "entry_date": "entry_date",
        "course": "course",
        "description": "description",
        "mail": "mail",
        "extra": "extra"
    }
    You don't need to send all the fields, only the ones you want to update
    If unkonwn fields are provided, a 400 error is returned
    """
    # Get the request data
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided for update'}), HTTPStatus.BAD_REQUEST

    # Check if the user has permission to update the member
    user_tags = session['tags'].split(',')
    if session['username'] != username:
        if not tags_handler.can(user_tags, 'edit_member'):
            return jsonify({'message': 'You do not have permission to update this member'}), HTTPStatus.FORBIDDEN
        if 'password' in data:
            if not tags_handler.can(user_tags, 'edit_password'):
                return jsonify({'message': 'You do not have permission to update the password'}), HTTPStatus.FORBIDDEN

    # Get the member ID from the username
    member_id = member_service.getMemberIdByUsername(username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), HTTPStatus.NOT_FOUND

    # Define valid columns
    valid_columns = {"istID", "memberNumber", "name", "username", "password", "entry_date", 
                    "exit_date", "course", "description", "mail", "extra"}

    # Check for invalid fields in the data
    invalid_fields = [key for key in data.keys() if key not in valid_columns]
    if invalid_fields:
        return jsonify({'message': 'Invalid fields provided', 'invalid_fields': invalid_fields}), HTTPStatus.NOT_FOUND

    # Call the editMember method and pass the valid fields that need to be updated
    update_success = member_service.editMember(member_id, **data)

    if not update_success[0]:
        return jsonify({'message': update_success[1]}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({'message': 'Member updated successfully!'}), HTTPStatus.OK


@bp.route('/<string:username>', methods=['DELETE'])
@login_required
@required_permission('delete_member', allow_self_action=True)
def delete_member(username):
    """
    Deletes a member with the username provided in the url
    Only users with the permission to delete a member can delete a member
    An error is returned if the member does not exist or the user does not have permission
    """
    # Does the user have permission to delete the member?
    member_id = member_service.getMemberIdByUsername(username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), HTTPStatus.NOT_FOUND 
    member_service.deleteMember(member_id)
    return jsonify({'message': 'Member deleted successfully!'}), HTTPStatus.OK

@bp.route('/<string:username>/projects', methods=['GET'])
@login_required
def get_member_projects(username):
    member_id = member_service.getMemberIdByUsername(username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), HTTPStatus.NOT_FOUND
    projects = member_project_service.listProjectsForMember(member_id)
    return jsonify(projects), HTTPStatus.OK

############# Tags #############
@bp.route('/<string:username>/tags', methods=['GET'])
@login_required
def get_member_tags(username):
    """
    Given a member username, returns the tags associated with the member
    In case the member does not exist, a 404 error is returned

    The returned information is in the following format:
    {
        "tags": "tag1,tag2,..."
    }
    """
    member_id = member_service.getMemberIdByUsername(username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), HTTPStatus.NOT_FOUND 
    tags = member_service.getMemberTags(username)
    return jsonify(tags), HTTPStatus.OK

@bp.route('/<string:username>/tags', methods=['POST'])
@login_required
def add_member_tag(username): 
    """
    Attempt to add a tag to a member
    Only users with the permission to add a tag can add a tag
    An error is returned if the member does not exist, the tag is already associated with the member or the user does not have permission
    You cannot add a tag with an highier permission level than your own

    The format is the folowing:
    {
        "tag": "tag"
    }
    """       
    # Get the request data
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided for tag addition'}), HTTPStatus.BAD_REQUEST
    if 'tag' not in data:
        return jsonify({'message': 'No tag provided for addition'}), HTTPStatus.BAD_REQUEST
    
    # Does the user have permission to add a tag to the member?
    user_tags = session['tags'].split(',')
    if not tags.can(user_tags, 'add_tag', tagToAdd=data['tag']):
        return jsonify({'message': 'You do not have permission to add that tag'}), HTTPStatus.FORBIDDEN

    # Get the member ID from the username
    member_id = member_service.getMemberIdByUsername(username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), HTTPStatus.NOT_FOUND

    # Check if the tag is already associated with the member
    tags = member_service.getTags(username)
    if data['tag'] in tags:
        return jsonify({'message': 'Tag already associated with member'})

    # Add the tag to the member
    ret = member_service.addTag(member_id, data['tag'])
    if not ret[0]:
        return jsonify({'message': ret[1]}), HTTPStatus.INTERNAL_SERVER_ERROR 
    return jsonify({'message': 'Tag added successfully!'}), HTTPStatus.OK

@bp.route('/<string:username>/tags', methods=['DELETE'])
@login_required
def remove_member_tag(username):
    """
    Attempts to remove a tag from a member
    Only users with the permission to remove a tag can remove a tag
    An error is returned if the member does not exist, the tag is not associated with the member or the user does not have permission
    
    The format is the folowing:
    {
        "tag": "tag"
    }
    """
    # Get the request data
    data = request.json
    if not data:
        return jsonify({'message': 'No data provided for tag removal'}), HTTPStatus.BAD_REQUEST
    if 'tag' not in data:
        return jsonify({'message': 'No tag provided for removal'}), HTTPStatus.BAD_REQUEST
    
    # Does the user have permission to remove a tag from the member?
    user_tags = session['tags'].split(',')
    if not tags.can(user_tags, 'add_tag', tagToAdd=data['tag']):
        return jsonify({'message': 'You do not have permission to remove that tag'}), HTTPStatus.FORBIDDEN

    # Get the member ID from the username
    member_id = member_service.getMemberIdByUsername(username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), HTTPStatus.NOT_FOUND 

    # Check if the tag is associated with the member
    tags = member_service.getTags(username)
    if data['tag'] not in tags:
        return jsonify({'message': 'Tag not associated with member'})

    # Remove the tag from the member
    ret = member_service.removeTag(member_id, data['tag'])
    if not ret[0]:
        return jsonify({'message': ret[1]}), HTTPStatus.INTERNAL_SERVER_ERROR
    return jsonify({'message': 'Tag removed successfully!'})
