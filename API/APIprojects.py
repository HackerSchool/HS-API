from flask import Blueprint, request, jsonify, session
# Importing the methods for the projects
from API import handlers
from Tags import Tags

# TODO: Implement the return messages for the API calls
# TODO: Change the routs to work with the project name and not the project id
# TODO: Associate the members with the projects
# TODO: Change/Return logo image for the project

############# Projects #############
def createProjectBlueprint(handlers: handlers.Handlers, login_required, tags: Tags):
    project_bp = Blueprint('projects', __name__)

    projectHandler = handlers.projectHandler
    memberProjectHandler = handlers.memberProjectHandler

    @project_bp.route('/projects', methods=['GET'])
    @login_required
    def get_projects():
        projects = projectHandler.listProjects()
        return jsonify(projects)
    
    @project_bp.route('/projects', methods=['POST'])
    @login_required
    def create_project():
        # Does the user have permition to create a project
        user_tags = session['tags'].split(',')
        if not tags.can(user_tags, 'create_project'):
            return jsonify({'message': 'You do not have permission to create a project'}), 403

        data = request.json
        required_fields = ['name', 'start_date', 'state', 'description']

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'message': 'Missing required fields', 'missing_fields': missing_fields}), 400

        projectHandler.createProject(data['name'], data['description'], data['start_date'], data['state'], None)
        return jsonify({'message': 'Project created successfully!'})
    
    @project_bp.route('/projects/<int:project_id>', methods=['GET'])
    @login_required
    def get_project(project_id):
        project_data = projectHandler.getProject(project_id)
        return jsonify(project_data)
    
    @project_bp.route('/projects/<int:project_id>', methods=['PUT'])
    @login_required
    def update_project(project_id):
        # Does the user have permition to update a project
        user_tags = session['tags'].split(',')
        if not tags.can(user_tags, 'edit_project'):
            return jsonify({'message': 'You do not have permission to edit a project'}), 403

        # Check if the project exists
        project = projectHandler.exists(project_id)
        if not project:
            return jsonify({'message': 'Project not found'}), 404

        # Define valid columns
        valid_columns = {'name', 'start_date', 'state', 'description'}
        # Check for invalid fields in the data
        data = request.json
        invalid_fields = [key for key in data.keys() if key not in valid_columns]
        if invalid_fields:
            return jsonify({'message': 'Invalid fields provided', 'invalid_fields': invalid_fields}), 400

        update_success = projectHandler.editProject(project_id, **data)
        if update_success:
            return jsonify({'message': 'Project updated successfully!'})
        else:
            return jsonify({'message': 'Failed to update project'}), 500
    
    @project_bp.route('/projects/<int:project_id>', methods=['DELETE'])
    @login_required
    def delete_project(project_id):
        # Does the user have permition to delete a project
        user_tags = session['tags'].split(',')
        if not tags.can(user_tags, 'delete_project'):
            # Check if the project exists
            project = projectHandler.getProject(project_id)
            if not project:
                return jsonify({'message': 'Project not found'}), 404
            return jsonify({'message': 'You do not have permission to delete a project'}), 403

        projectHandler.deleteProject(project_id)
        return jsonify({'message': 'Project deleted successfully!'})
    
    @project_bp.route('/projects/<int:project_id>/members', methods=['GET'])
    @login_required
    def get_project_members(project_id):
        members = memberProjectHandler.listMembers(project_id)
        return jsonify(members)
    
    return project_bp