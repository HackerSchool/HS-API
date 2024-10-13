from flask import Blueprint, request, jsonify, session
# Importing the methods for the members
from API import handlers
from Tags import Tags

from io import BytesIO
from PIL import Image
import base64

def isALink(link):
    if link.startswith("http://") or link.startswith("https://"):
        return True
    return False

############# Logos #############
def createLogosBlueprint(handlers: handlers.Handlers, login_required, tags: Tags):
    logo_bp = Blueprint('logos', __name__)

    memberHandler = handlers.memberHandler
    projectHandler = handlers.projectHandler
    logosHandler = handlers.logosHandler

    ############# Members #############
        # Get member logo
    @logo_bp.route('/members/<string:username>/logo', methods=['GET'])
    @login_required
    def getMemberLogo(username):
        if not memberHandler.getMemberIdByUsername(username):
            return jsonify({"error": "Member not found"}), 404

        # We ask the database for the logo
        logo_str = memberHandler.getLogo(username)
        # If it's none means there is no logo
        if logo_str is None:
            return jsonify({"error": "Logo not found"}), 404
        # The logo can be a simple url, we send it back
        if isALink(logo_str):
            return jsonify({"link": logo_str}), 200
        # If we are here means the image should be in the file system
        logo = logosHandler.getLogo(username)
        if logo is None:
            return jsonify({"error": "Logo not found"}), 404
        
        image_data = base64.b64encode(logo).decode('utf-8')
        return jsonify({"image": image_data}), 200

        # Set member logo
    @logo_bp.route('/members/<string:username>/logo', methods=['POST'])
    @login_required
    def setMemberLogo(username):
        if not memberHandler.getMemberIdByUsername(username):
            return jsonify({"error": "Member not found"}), 404
        
        # Check if the user can edit members, or if the user is the member itself
        if not tags.can(session['tags'].split(','), 'edit_members') and session['username'] != username:
            return jsonify({"error": "Unauthorized"}), 403

        # If the user sent a link we just update the database
        if 'link' in request.json:
            if not isALink(request.json['link']):
                return jsonify({"error": "Invalid link"}), 400
            memberHandler.setLogo(username, request.json['link'])
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
        logosHandler.writeLogo(username, binary_image_data)

        memberHandler.setLogo(username, 'in_filesystem')
        return jsonify({"message": "Logo updated"}), 200
    
    ############# Projects #############
        # Get project logo
    @logo_bp.route('/projects/<int:proj_id>/logo', methods=['GET'])
    @login_required
    def getProjectLogo(proj_id):
        if not projectHandler.exists(proj_id):
            return jsonify({"error": "Project not found"}), 404

        # We ask the database for the logo
        logo_str = projectHandler.getLogo(proj_id)
        if logo_str is None:
            return jsonify({"error": "Logo not found"}), 404
        # The logo can be a simple url, we send it back
        if isALink(logo_str):
            return jsonify({"link": logo_str}), 200
        # If we are here means the image should be in the file system
        logo = logosHandler.getLogo(proj_id)
        if logo is None:
            return jsonify({"error": "Logo not found"}), 404
        
        image_data = base64.b64encode(logo).decode('utf-8')
        return jsonify({"image": image_data}), 200
    
        # Set project logo
    @logo_bp.route('/projects/<int:proj_id>/logo', methods=['POST'])
    @login_required
    def setProjectLogo(proj_id):
        if not projectHandler.exists(proj_id):
            return jsonify({"error": "Project not found"}), 404
        
        # Check if the user can edit projects
        if not tags.can(session['tags'].split(','), 'edit_projects'):
            return jsonify({"error": "Unauthorized"}), 403

        # The user can send an url
        if 'link' in request.json:
            if not isALink(request.json['link']):
                return jsonify({"error": "Invalid link"}), 400
            projectHandler.setLogo(proj_id, request.json['link'])
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
        logosHandler.writeLogo(proj_id, binary_image_data)

        projectHandler.setLogo(proj_id, 'in_filesystem')
        return jsonify({"message": "Logo updated"}), 200
    
    return logo_bp