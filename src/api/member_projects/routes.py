from flask import request, jsonify

from api.member_projects import bp
from api.decorators import login_required
from api.extensions import member_service, member_project_service

@bp.route('/link/<string:username>/<int:proj_id>', methods=['POST'])
@login_required
def linkMemberProject(username, proj_id):
    user_id = member_service.getMemberIdByUsername(username)
    if not user_id:
        return jsonify({"error": "Member not found"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Check if the data contains the following fields
    required_fields = ['entry_date', 'contributions']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Field '{field}' is required"}), 400
    # Check if there is exit_date
    if 'exit_date' in data:
        exit_date = data['exit_date']
    else:
        exit_date = ""
        
    ret = member_project_service.associateMemberWithProject(user_id, proj_id, data['entry_date'], data['contributions'], exit_date)
    if not ret[0]:
        return jsonify({"error": ret[1]}), 400
    return jsonify({"success": ret[1]}), 200

@bp.route('/link/<string:username>/<int:proj_id>', methods=['PUT'])
@login_required
def editMemberProject(username, proj_id):
    user_id = member_service.getMemberIdByUsername(username)
    if not user_id:
        return jsonify({"error": "Member not found"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Verify that we only allow the following fields to be updated
    allowed_fields = ['entry_date', 'contributions', 'exit_date']
    for field in data.keys():
        if field not in allowed_fields:
            return jsonify({"error": f"Field '{field}' is not allowed"}), 400
    
    ret = member_project_service.editMemberProjectRelation(user_id, proj_id, **data)
    if not ret[0]:
        return jsonify({"error": ret[1]}), 400
    return jsonify({"success": ret[1]}), 200

@bp.route('/link/<string:username>/<int:proj_id>', methods=['DELETE'])
@login_required
def unlinkMemberProject(username, proj_id):
    user_id = member_service.getMemberIdByUsername(username)
    if not user_id:
        return jsonify({"error": "Member not found"}), 404
    
    ret = member_project_service.deleteMemberProjectRelation(user_id, proj_id)
    if not ret[0]:
        return jsonify({"error": ret[1]}), 400
    return jsonify({"success": ret[1]}), 200
