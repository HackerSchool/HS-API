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
        
        data = request.json
        memberHandler.createMember(data['username'], data['role_id'], data['name'], data['username'], data['password'], data['join_date'], data['department'], data['role'], data['tags'], data['logo'])
        return jsonify({'message': 'Member created successfully!'})

    @members_bp.route('/members/<string:member_username>', methods=['GET'])
    @login_required
    def get_member(member_username):
        member_data = memberHandler.getMemberInfo(member_username)
        return jsonify(member_data)

    @members_bp.route('/members/<string:member_username>', methods=['PUT'])
    @login_required
    def update_member(member_username):
        # Does the user have permission to update the member?
        user_tags = session['tags'].split(',')
        if not tags.can(user_tags, 'update_member') and username != member_username:
            return jsonify({'message': 'You do not have permission to update a member'}), 403

        data = request.json
        member_id = memberHandler.getMemberIdByUsername(member_username)
        if member_id is None:
            return jsonify({'message': 'Member not found'}), 404
        memberHandler.updateMember(member_id, data['name'], data['username'], data['password'], data['join_date'], data['department'], data['role'], data['tags'], data['logo'])
        return jsonify({'message': 'Member updated successfully!'})

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