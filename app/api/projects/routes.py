from flask import session, request, jsonify

from app.api.projects import bp
from app.api.decorators import login_required
from app.api.extensions import project_service, member_project_service, tags_handler

@bp.route('/projects', methods=['GET'])
@login_required
def get_projects():
    """
    Returns all projects in the database in a list of lists, each list contains the information of a project
    """
    projects = project_service.listProjects()
    return jsonify(projects)

# Create a project
@bp.route('/projects', methods=['POST'])
@login_required
def create_project():
    """
    Creates a project in the database with the information provided in the request body
    Only users with the permission to create a project can create a project
    An error is returned if the required fields are not provided or the user does not have permission

    The format is the folowing:
    {
        "name": "name",
        "start_date": "start_date",
        "state": "state",
        "description": "description"
    }
    """
    # Does the user have permition to create a project
    user_tags = session['tags'].split(',')
    if not tags_handler.can(user_tags, 'create_project'):
        return jsonify({'message': 'You do not have permission to create a project'}), 403

    data = request.json
    required_fields = ['name', 'start_date', 'state', 'description']

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'message': 'Missing required fields', 'missing_fields': missing_fields}), 400

    ret = project_service.createProject(data['name'], data['description'], data['start_date'], data['state'], None)
    if not ret[0]:
        return jsonify({'message': ret[1]}), 500
    return jsonify({'message': 'Project created successfully!'})

# Get the data of a specific project
@bp.route('/projects/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """
    Returns a project with the id provided in the url
    In case the project does not exist, a 404 error is returned
    """
    project_data = project_service.getProjectInfo(project_id)
    if not project_data:
        return jsonify({'message': 'Project not found'}), 404
    return jsonify(project_data)

@bp.route('/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """
    Updates the information of a project with the id provided in the url
    Only users with the permission to edit a project can update a project
    An error is returned if the project does not exist, the user does not have permission or the data provided is invalid

    The format is the folowing:
    {
        "name": "name",
        "start_date": "start_date",
        "state": "state",
        "description": "description"
    }
    You don't need to send all the fields, only the ones you want to update
    If unkonwn fields are provided, a 400 error is returned
    """
    # Does the user have permition to update a project
    user_tags = session['tags'].split(',')
    if not tags_handler.can(user_tags, 'edit_project'):
        return jsonify({'message': 'You do not have permission to edit a project'}), 403

    # Check if the project exists
    project = project_service.exists(project_id)
    if not project:
        return jsonify({'message': 'Project not found'}), 404

    # Define valid columns
    valid_columns = {'name', 'start_date', 'state', 'description'}
    # Check for invalid fields in the data
    data = request.json
    invalid_fields = [key for key in data.keys() if key not in valid_columns]
    if invalid_fields:
        return jsonify({'message': 'Invalid fields provided', 'invalid_fields': invalid_fields}), 400

    update_success = project_service.editProject(project_id, **data)
    if update_success[0]:
        return jsonify({'message': 'Project updated successfully!'})
    else:
        return jsonify({'message': update_success[1]}), 500

@bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """
    Deletes a project with the id provided in the url and removes the associations with the members
    Only users with the permission to delete a project can delete a project
    An error is returned if the project does not exist or the user does not have permission
    """
    # Does the user have permition to delete a project
    user_tags = session['tags'].split(',')
    if not tags_handler.can(user_tags, 'delete_project'):
        # Check if the project exists
        project = project_service.getProject(project_id)
        if not project:
            return jsonify({'message': 'Project not found'}), 404
        return jsonify({'message': 'You do not have permission to delete a project'}), 403

    project_service.deleteProject(project_id)
    return jsonify({'message': 'Project deleted successfully!'})

@bp.route('/projects/<int:project_id>/members', methods=['GET'])
@login_required
def get_project_members(project_id):
    members = member_project_service.listMembersForProject(project_id)
    return jsonify(members)
