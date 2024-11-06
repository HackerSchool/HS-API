from flask import jsonify, request, send_file
from http import HTTPStatus

from app.extensions import logos_handler

from app.logos.exceptions import InvalidContentTypeError, LogoNotFoundError, InvalidLogoTypeError

from app.services import member_service, project_service

from app.api.logos import bp
from app.api.decorators import login_required, required_permission
from app.api.logos.utils import *


################################################################################
#################################### Members ###################################
################################################################################
@bp.route('/members/<string:username>/logo', methods=['GET'])
# @login_required
def get_member_logo(username):
    """ Retrieve logo of a member given its' username """
    # TODO add external reference support
    if member_service.get_member_by_username(username) is None:
        return jsonify({"error": "Member does not exist"}), HTTPStatus.NOT_FOUND

    logo_path: str 
    mimetype: str
    try:
        logo_path, mimetype = logos_handler.get_logo(username, logo_type="member")
    except LogoNotFoundError as e:
        return jsonify({"error": f"Logo not found for user {e.resource_id}"}), HTTPStatus.NOT_FOUND
    except InvalidLogoTypeError as e:
        # this shouldn't happen
        return jsonify({"error": f"Internal"}), HTTPStatus.INTERNAL_SERVER_ERROR

    # TODO add Etag support
    return send_file(path_or_file=logo_path, mimetype=mimetype)

# Set member logo
@bp.route('/members/<string:username>/logo', methods=['POST'])
# @login_required
# @required_permission('edit_member', allow_self_action=True)
def set_member_logo(username):
    """ Set the logo of a member given its' username """
    if 'file' not in request.files or request.files['file'] == '':
        return jsonify({"error": "Missing file!"}), HTTPStatus.BAD_REQUEST

    # TODO add external reference support
    if member_service.get_member_by_username(username) is None:
        return jsonify({"error": "Member not found"}), HTTPStatus.NOT_FOUND
    
    try:
        logos_handler.save_logo(username, request.files['file'], logo_type="member")
    except InvalidContentTypeError as e:
        return jsonify({"error": f"Invalid Content Type {e.content_type}"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    except InvalidLogoTypeError as e:
        # this shouldn't happen
        return jsonify({"error": f"Internal"}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({"message": "Logo uploaded!"}), HTTPStatus.OK

################################################################################
################################### Projects ###################################
################################################################################
@bp.route('/projects/<string:proj_name>/logo', methods=['GET'])
# @login_required
def get_project_logo(proj_name):
    """ Retrieve logo of a project given its' ID """
    if project_service.get_project_by_name(proj_name) is None:
        return jsonify({"error": "Project not found"}), HTTPStatus.NOT_FOUND

    logo_path: str 
    mimetype: str
    try:
        logo_path, mimetype = logos_handler.get_logo(proj_name, logo_type="project")
    except LogoNotFoundError as e:
        return jsonify({"error": f"Logo not found for project {e.resource_id}"}), HTTPStatus.NOT_FOUND
    except InvalidLogoTypeError as e:
        # this shouldn't happen
        return jsonify({"error": f"Internal"}), HTTPStatus.INTERNAL_SERVER_ERROR

    # TODO add Etag support
    return send_file(path_or_file=logo_path, mimetype=mimetype)

# Set project logo
@bp.route('/projects/<string:proj_name>/logo', methods=['POST'])
# @login_required
# @required_permission('edit_project')
def set_project_logo(proj_name):
    """ Set the logo of a project given its' ID """
    if 'file' not in request.files or request.files['file'] == '':
        return jsonify({"error": "Missing file!"}), HTTPStatus.BAD_REQUEST

    if project_service.exists(proj_name) is None:
        return jsonify({"error": "Project not found"}), HTTPStatus.NOT_FOUND

    try:
        logos_handler.save_logo(proj_name, request.files['file'], logo_type="project")
    except InvalidContentTypeError as e:
        return jsonify({"error": f"Invalid Content Type {e.content_type}"}), HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    except InvalidLogoTypeError as e:
        # this shouldn't happen
        return jsonify({"error": f"Internal"}), HTTPStatus.INTERNAL_SERVER_ERROR

    return jsonify({"message": "Logo uploaded!"}), HTTPStatus.OK
