from flask import Blueprint, request, jsonify, session
# Importing the methods for the members
from API import handlers
from Tags import Tags

############# Members #############
def createMembersBlueprint(handlers: handlers.Handlers, login_required, tags: Tags):
    members_bp = Blueprint('members', __name__)

    memberHandler = handlers.memberHandler
    memberProjectHandler = handlers.memberProjectHandler

    @members_bp.route('/members', methods=['GET'])
    @login_required
    def get_members():
        members = memberHandler.listMembers()
        return jsonify(members)

    @members_bp.route('/members', methods=['POST'])
    @login_required
    def create_member():
        # Does the user have permission to create a member?
        user_tags = session['tags'].split(',')
        if not tags.can(user_tags, 'create_member'):
            return jsonify({'message': 'You do not have permission to create a member'}), 403
        
        # Validate request data
        data = request.json
        required_fields = ['istID', 'memberNumber', 'name', 'username', 'password', 'join_date', 'course', 'description', 'mail']

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': 'Missing required fields', 'missing_fields': missing_fields}), 400

        # Proceed if all required fields are present
        ret = memberHandler.createMember(data['istID'], data['memberNumber'], data['name'], data['username'], 
                                data['password'], data['join_date'], data['course'], 
                                data['description'], data['mail'], '{}', None, 'member')
        if not ret[0]:
            return jsonify({'message': ret[1]}), 400
        return jsonify({'message': 'Member created successfully!'})

    @members_bp.route('/members/<string:member_username>', methods=['GET'])
    @login_required
    def get_member(member_username):
        member_data = memberHandler.getMemberInfo(member_username)
        return jsonify(member_data)

    @members_bp.route('/members/<string:member_username>', methods=['PUT'])
    @login_required
    def update_member(member_username):
        # Get the request data
        data = request.json
        if not data:
            return jsonify({'message': 'No data provided for update'}), 400

        # Check if the user has permission to update the member
        user_tags = session['tags'].split(',')
        if session['username'] != member_username:
            if not tags.can(user_tags, 'edit_member'):
                return jsonify({'message': 'You do not have permission to update this member'}), 403
            if 'password' in data:
                if not tags.can(user_tags, 'edit_password'):
                    return jsonify({'message': 'You do not have permission to update the password'}), 403

        # Get the member ID from the username
        member_id = memberHandler.getMemberIdByUsername(member_username)
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
        update_success = memberHandler.editMember(member_id, **data)

        if update_success[0]:
            return jsonify({'message': 'Member updated successfully!'})
        else:
            return jsonify({'message': update_success[1]}), 500


    @members_bp.route('/members/<string:member_username>', methods=['DELETE'])
    @login_required
    def delete_member(member_username):
        # Does the user have permission to delete the member?
        user_tags = session['tags'].split(',')
        if not tags.can(user_tags, 'delete_member'):
            return jsonify({'message': 'You do not have permission to delete a member'}), 403
        
        member_id = memberHandler.getMemberIdByUsername(member_username)
        if member_id is None:
            return jsonify({'message': 'Member not found'}), 404
        memberHandler.deleteMember(member_id)
        return jsonify({'message': 'Member deleted successfully!'})

    @members_bp.route('/members/<string:member_username>/projects', methods=['GET'])
    @login_required
    def get_member_projects(member_username):
        member_id = memberHandler.getMemberIdByUsername(member_username)
        if member_id is None:
            return jsonify({'message': 'Member not found'}), 404
        projects = memberProjectHandler.getMemberProjects(member_id)
        return jsonify(projects)
    
    ############# Tags #############
    @members_bp.route('/members/<string:member_username>/tags', methods=['GET'])
    @login_required
    def get_member_tags(member_username):
        member_id = memberHandler.getMemberIdByUsername(member_username)
        if member_id is None:
            return jsonify({'message': 'Member not found'}), 404
        tags = memberHandler.getMemberTags(member_username)
        return jsonify(tags)
    
    @members_bp.route('/members/<string:member_username>/tags', methods=['POST'])
    @login_required
    def add_member_tag(member_username):        
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
        member_id = memberHandler.getMemberIdByUsername(member_username)
        if member_id is None:
            return jsonify({'message': 'Member not found'}), 404

        # Check if the tag is already associated with the member
        tags = memberHandler.getTags(member_username)
        if data['tag'] in tags:
            return jsonify({'message': 'Tag already associated with member'})

        # Add the tag to the member
        ret = memberHandler.addTag(member_id, data['tag'])
        if not ret[0]:
            return jsonify({'message': ret[1]}), 500
        return jsonify({'message': 'Tag added successfully!'})
    
    @members_bp.route('/members/<string:member_username>/tags', methods=['DELETE'])
    @login_required
    def remove_member_tag(member_username):
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
        member_id = memberHandler.getMemberIdByUsername(member_username)
        if member_id is None:
            return jsonify({'message': 'Member not found'}), 404

        # Check if the tag is associated with the member
        tags = memberHandler.getTags(member_username)
        if data['tag'] not in tags:
            return jsonify({'message': 'Tag not associated with member'})

        # Remove the tag from the member
        ret = memberHandler.removeTag(member_id, data['tag'])
        if not ret[0]:
            return jsonify({'message': ret[1]}), 500
        return jsonify({'message': 'Tag removed successfully!'})

    return members_bp