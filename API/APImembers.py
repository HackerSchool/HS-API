from flask import Blueprint, request, jsonify, session
# Importing the methods for the members
from API import handlers
from Tags import Tags

# AVISO À NAVEGAÇÃO
# As routs aqui presentes apresentam cabaçalhos que não fazem muito sentido
# no contexto da chamada à base de dados. Por isso ainda existe muita coisa a ser
# feita, nomeadamente:
# - Ajustar os cabaçalhos das rotas
# - DEFINIR QUAL O CORPO DOS REQUESTS/POSTS

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
        required_fields = ['istID', 'memberNumber', 'name', 'username', 'password', 'join_date', 'course', 'description']

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': 'Missing required fields', 'missing_fields': missing_fields}), 400

        # Proceed if all required fields are present
        memberHandler.createMember(data['istID'], data['memberNumber'], data['name'], data['username'], 
                                data['password'], data['join_date'], data['course'], 
                                data['description'], '{}', None, 'member')
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
                        "exit_date", "course", "description", "extra"}

        # Check for invalid fields in the data
        invalid_fields = [key for key in data.keys() if key not in valid_columns]
        if invalid_fields:
            return jsonify({'message': 'Invalid fields provided', 'invalid_fields': invalid_fields}), 400

        # Call the editMember method and pass the valid fields that need to be updated
        update_success = memberHandler.editMember(member_id, **data)

        if update_success:
            return jsonify({'message': 'Member updated successfully!'})
        else:
            return jsonify({'message': 'Failed to update member'}), 500


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
    
    return members_bp