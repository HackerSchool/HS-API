from flask import session, jsonify, request

from api.members import bp
from api.decorators import login_required
from api.extensions import member_service, member_project_service, tags_handler

@bp.route('/members', methods=['POST'])
@login_required
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
            "join_date": "join_date",
            "course": "course",
            "description": "description",
            "mail": "mail"
        }
        """
        # Does the user have permission to create a member?
    user_tags = session['tags'].split(',')
    if not tags_handler.can(user_tags, 'create_member'):
        return jsonify({'message': 'You do not have permission to create a member'}), 403
    
    # Validate request data
    data = request.json
    required_fields = ['istID', 'memberNumber', 'name', 'username', 'password', 'join_date', 'course', 'description', 'mail']

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'message': 'Missing required fields', 'missing_fields': missing_fields}), 400

    # Proceed if all required fields are present
    ret = member_service.createMember(data['istID'], data['memberNumber'], data['name'], data['username'], 
                            data['password'], data['join_date'], data['course'], 
                            data['description'], data['mail'], '{}', None, 'member')
    if not ret[0]:
        return jsonify({'message': ret[1]}), 400
    return jsonify({'message': 'Member created successfully!'})

@bp.route('/members/<string:member_username>', methods=['GET'])
@login_required
def get_member(member_username):
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
    member_data = member_service.getMemberInfo(member_username)

    # If the member does not exist
    if not member_data:
        return jsonify({'message': 'No member with that username!'}), 404
    return jsonify(member_data)

@bp.route('/members/<string:member_username>', methods=['PUT'])
@login_required
def update_member(member_username):
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
        return jsonify({'message': 'No data provided for update'}), 400

    # Check if the user has permission to update the member
    user_tags = session['tags'].split(',')
    if session['username'] != member_username:
        if not tags_handler.can(user_tags, 'edit_member'):
            return jsonify({'message': 'You do not have permission to update this member'}), 403
        if 'password' in data:
            if not tags_handler.can(user_tags, 'edit_password'):
                return jsonify({'message': 'You do not have permission to update the password'}), 403

    # Get the member ID from the username
    member_id = member_service.getMemberIdByUsername(member_username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), 404

    # Define valid columns
    valid_columns = {"istID", "memberNumber", "name", "username", "password", "entry_date", 
                    "exit_date", "course", "description", "mail", "extra"}

    # Check for invalid fields in the data
    invalid_fields = [key for key in data.keys() if key not in valid_columns]
    if invalid_fields:
        return jsonify({'message': 'Invalid fields provided', 'invalid_fields': invalid_fields}), 400

    # Call the editMember method and pass the valid fields that need to be updated
    update_success = member_service.editMember(member_id, **data)

    if update_success[0]:
        return jsonify({'message': 'Member updated successfully!'})
    else:
        return jsonify({'message': update_success[1]}), 500


@bp.route('/members/<string:member_username>', methods=['DELETE'])
@login_required
def delete_member(member_username):
    """
    Deletes a member with the username provided in the url
    Only users with the permission to delete a member can delete a member
    An error is returned if the member does not exist or the user does not have permission
    """
    # Does the user have permission to delete the member?
    user_tags = session['tags'].split(',')
    if not tags_handler.can(user_tags, 'delete_member'):
        return jsonify({'message': 'You do not have permission to delete a member'}), 403
    
    member_id = member_service.getMemberIdByUsername(member_username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), 404
    member_service.deleteMember(member_id)
    return jsonify({'message': 'Member deleted successfully!'})

@bp.route('/members/<string:member_username>/projects', methods=['GET'])
@login_required
def get_member_projects(member_username):
    member_id = member_service.getMemberIdByUsername(member_username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), 404
    projects = member_project_service.listProjectsForMember(member_id)
    return jsonify(projects)

############# Tags #############
@bp.route('/members/<string:member_username>/tags', methods=['GET'])
@login_required
def get_member_tags(member_username):
    """
    Given a member username, returns the tags associated with the member
    In case the member does not exist, a 404 error is returned

    The returned information is in the following format:
    {
        "tags": "tag1,tag2,..."
    }
    """
    member_id = member_service.getMemberIdByUsername(member_username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), 404
    tags = member_service.getMemberTags(member_username)
    return jsonify(tags)

@bp.route('/members/<string:member_username>/tags', methods=['POST'])
@login_required
def add_member_tag(member_username): 
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
        return jsonify({'message': 'No data provided for tag addition'}), 400
    if 'tag' not in data:
        return jsonify({'message': 'No tag provided for addition'}), 400
    
    # Does the user have permission to add a tag to the member?
    user_tags = session['tags'].split(',')
    if not tags.can(user_tags, 'add_tag', tagToAdd=data['tag']):
        return jsonify({'message': 'You do not have permission to add that tag'}), 403

    # Get the member ID from the username
    member_id = member_service.getMemberIdByUsername(member_username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), 404

    # Check if the tag is already associated with the member
    tags = member_service.getTags(member_username)
    if data['tag'] in tags:
        return jsonify({'message': 'Tag already associated with member'})

    # Add the tag to the member
    ret = member_service.addTag(member_id, data['tag'])
    if not ret[0]:
        return jsonify({'message': ret[1]}), 500
    return jsonify({'message': 'Tag added successfully!'})

@bp.route('/members/<string:member_username>/tags', methods=['DELETE'])
@login_required
def remove_member_tag(member_username):
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
        return jsonify({'message': 'No data provided for tag removal'}), 400
    if 'tag' not in data:
        return jsonify({'message': 'No tag provided for removal'}), 400
    
    # Does the user have permission to remove a tag from the member?
    user_tags = session['tags'].split(',')
    if not tags.can(user_tags, 'add_tag', tagToAdd=data['tag']):
        return jsonify({'message': 'You do not have permission to remove that tag'}), 403

    # Get the member ID from the username
    member_id = member_service.getMemberIdByUsername(member_username)
    if member_id is None:
        return jsonify({'message': 'Member not found'}), 404

    # Check if the tag is associated with the member
    tags = member_service.getTags(member_username)
    if data['tag'] not in tags:
        return jsonify({'message': 'Tag not associated with member'})

    # Remove the tag from the member
    ret = member_service.removeTag(member_id, data['tag'])
    if not ret[0]:
        return jsonify({'message': ret[1]}), 500
    return jsonify({'message': 'Tag removed successfully!'})
