import base64
from io import BytesIO
from PIL import Image

from flask import jsonify, session, request

from app.api.logos import bp
from app.api.decorators import login_required
from app.api.extensions import member_service, project_service, logos_handler, tags_handler

from app.api.logos.utils import *

@bp.route('/members/<string:username>/logo', methods=['GET'])
@login_required
def getMemberLogo(username):
    """
    Given a username, returns the logo of the member

    Return format:
    {
        "link": "url"  # If the logo is a link
    }
    or
    {
        "image": base64 format  # If the logo is in the file system
    """
    if not member_service.getMemberIdByUsername(username):
        return jsonify({"error": "Member not found"}), 404

    # We ask the database for the logo
    logo_str = member_service.getLogo(username)
    # If it's none means there is no logo
    if logo_str is None:
        return jsonify({"error": "Logo not found"}), 404
    # The logo can be a simple url, we send it back
    if isALink(logo_str):
        return jsonify({"link": logo_str}), 200
    # If we are here means the image should be in the file system
    logo = logos_handler.getLogo(username)
    if logo is None:
        return jsonify({"error": "Logo not found"}), 404
    
    image_data = base64.b64encode(logo).decode('utf-8')
    return jsonify({"image": image_data}), 200

    # Set member logo
@bp.route('/members/<string:username>/logo', methods=['POST'])
@login_required
def setMemberLogo(username):
    """
    Sets the logo of a member given a username

    The format is the following:
    {
        "link": "url"  # If the logo is a link
    }
    or
    {
        "image": base64 format # If the logo is in the file system
    """
    if not member_service.getMemberIdByUsername(username):
        return jsonify({"error": "Member not found"}), 404
    
    # Check if the user can edit members, or if the user is the member itself
    if not tags_handler.can(session['tags'].split(','), 'edit_members') and session['username'] != username:
        return jsonify({"error": "Unauthorized"}), 403

    # If the user sent a link we just update the database
    if 'link' in request.json:
        if not isALink(request.json['link']):
            return jsonify({"error": "Invalid link"}), 400
        member_service.setLogo(username, request.json['link'])
        return jsonify({"message": "Logo updated"}), 200
    
    # The user sent an image, let's check if it's valid
    if 'image' not in request.json:
        return jsonify({"error": "No image provided"}), 400
    image_data = request.json['image']
    try:
        image = Image.open(BytesIO(base64.b64decode(image_data)))
    except:
        return jsonify({"error": "Invalid image"}), 400

    if image.format != 'PNG':
        return jsonify({"error": "Invalid image format"}), 400

    # Decode base64 back to binary before saving the image
    binary_image_data = base64.b64decode(image_data)
    logos_handler.writeLogo(username, binary_image_data)

    member_service.setLogo(username, 'in_filesystem')
    return jsonify({"message": "Logo updated"}), 200

############# Projects #############
    # Get project logo
@bp.route('/projects/<int:proj_id>/logo', methods=['GET'])
@login_required
def getProjectLogo(proj_id):
    """
    Given a project id, returns the logo of the project

    Return format:
    {
        "link": "url"  # If the logo is a link
    }
    or
    {
        "image": base64 format # If the logo is in the file system
    }
    """
    if not project_service.exists(proj_id):
        return jsonify({"error": "Project not found"}), 404

    # We ask the database for the logo
    logo_str = project_service.getLogo(proj_id)
    if logo_str is None:
        return jsonify({"error": "Logo not found"}), 404
    # The logo can be a simple url, we send it back
    if isALink(logo_str):
        return jsonify({"link": logo_str}), 200
    # If we are here means the image should be in the file system
    logo = logos_handler.getLogo(proj_id)
    if logo is None:
        return jsonify({"error": "Logo not found"}), 404
    
    image_data = base64.b64encode(logo).decode('utf-8')
    return jsonify({"image": image_data}), 200

    # Set project logo
@bp.route('/projects/<int:proj_id>/logo', methods=['POST'])
@login_required
def setProjectLogo(proj_id):
    """
    Sets the logo of a project given a project id

    The format is the following:
    {
        "link": "url"  # If the logo is a link
    }
    or
    {
        "image": base64 format # If the logo is in the file system
    }
    """
    if not project_service.exists(proj_id):
        return jsonify({"error": "Project not found"}), 404
    
    # Check if the user can edit projects
    if not tags_handler.can(session['tags'].split(','), 'edit_projects'):
        return jsonify({"error": "Unauthorized"}), 403

    # The user can send an url
    if 'link' in request.json:
        if not isALink(request.json['link']):
            return jsonify({"error": "Invalid link"}), 400
        project_service.setLogo(proj_id, request.json['link'])
        return jsonify({"message": "Logo updated"}), 200

    if 'image' not in request.json:
        return jsonify({"error": "No image provided"}), 400
    # The user sent an image, let's check if it's valid
    image_data = request.json['image']
    try:
        image = Image.open(BytesIO(base64.b64decode(image_data)))
    except:
        return jsonify({"error": "Invalid image"}), 400

    if image.format != 'PNG':
        return jsonify({"error": "Invalid image format"}), 400

    # Decode base64 back to binary before saving the image
    binary_image_data = base64.b64decode(image_data)
    logos_handler.writeLogo(proj_id, binary_image_data)

    project_service.setLogo(proj_id, 'in_filesystem')
    return jsonify({"message": "Logo updated"}), 200
