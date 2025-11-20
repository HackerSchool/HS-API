import os.path
from http import HTTPStatus

from flask import Blueprint
from flask import abort
from flask import request
from flask import send_file

from app.auth import AuthController

from app.repositories.project_repository import ProjectRepository
from app.repositories.member_repository import MemberRepository

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MIMETYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg"
}

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_images_bp(images_path: str, member_repo: MemberRepository, project_repo: ProjectRepository, auth_controller: AuthController):
    members_images_path = os.path.join(images_path, "members")
    projects_images_path = os.path.join(images_path, "projects")
    if not os.path.exists(members_images_path):
        os.makedirs(members_images_path)
    if not os.path.exists(projects_images_path):
        os.makedirs(projects_images_path)

    bp = Blueprint("images", __name__)

    @bp.route("/members/<username>/image", methods=["GET"])
    @auth_controller.requires_permission(general="member:read")
    def get_member_image(username):
        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Member with username '{username}' not found")

        for ext in ALLOWED_EXTENSIONS:
            file_name = member.ist_id + "." + ext
            path = os.path.join(members_images_path, file_name)
            if os.path.exists(path):
                return send_file(path, mimetype=MIMETYPES[ext])

        return abort(HTTPStatus.NOT_FOUND, description=f"Member '{username}' image not found")

    @bp.route("/projects/<slug>/image", methods=["GET"])
    @auth_controller.requires_permission(general="project:read")
    def get_project_image(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Project '{slug}' not found")

        for ext in ALLOWED_EXTENSIONS:
            file_name = project.name + "." + ext
            path = os.path.join(projects_images_path, file_name)
            if os.path.exists(path):
                return send_file(path, mimetype=MIMETYPES[ext])

        return abort(HTTPStatus.NOT_FOUND, description=f"Project {slug} image not found")

    @bp.route("/members/<username>/image", methods=["POST"])
    @auth_controller.requires_permission(general="member:update")
    def upload_member_image(username):
        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Member with username '{username}' not found")

        if 'file' not in request.files or not request.files['file'].filename:
            return abort(HTTPStatus.BAD_REQUEST, description=f"Missing file part")

        file = request.files['file']
        if not allowed_file(file.filename):
            return abort(HTTPStatus.BAD_REQUEST, description=f"Invalid image extension, only allowed :{ALLOWED_EXTENSIONS}")

        _, ext = os.path.splitext(file.filename)
        file.save(os.path.join(members_images_path, member.ist_id + ext))
        return {"description": "Member image uploaded successfully", "username": member.username}

    @bp.route("/projects/<slug>/image", methods=["POST"])
    @auth_controller.requires_permission(general="project:update", project="update")
    def upload_project_image(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Project '{slug}' not found")

        if 'file' not in request.files or not request.files['file'].filename:
            return abort(HTTPStatus.BAD_REQUEST, description=f"Missing file part")

        file = request.files['file']
        if not allowed_file(file.filename):
            return abort(HTTPStatus.BAD_REQUEST, description=f"Invalid image extension, only allowed :{ALLOWED_EXTENSIONS}")

        _, ext = os.path.splitext(file.filename)
        file.save(os.path.join(projects_images_path, project.slug + ext))
        return {"description": "Project image uploaded successfully", "name": project.name}

    return bp
