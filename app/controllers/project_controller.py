from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import abort

from app.access import AccessController
from app.utils import slugify

from app.schemas.project_schema import ProjectSchema
from app.schemas.update_project_schema import UpdateProjectSchema

from app.repositories.project_repository import ProjectRepository

from app.models.project_model import Project

from app.decorators import transactional
from app.extensions import db


def create_project_bp(*, project_repo: ProjectRepository, access_controller: AccessController):
    bp = Blueprint("projects", __name__)

    @bp.route("/projects", methods=["POST"])
    @access_controller.requires_permission(general="project:create")
    @transactional
    def create_project():
        project_data = ProjectSchema(**request.json)
        if project_repo.get_project_by_name(project_data.name) is not None:
            return abort(HTTPStatus.CONFLICT, description=f'Project with name "{project_data.name}" already exists')

        slug = slugify(project_data.name)
        if project_repo.get_project_by_slug(slug):
            return abort(HTTPStatus.CONFLICT,
                         description=f'A slug already exists for this name, please pick a new one: "{project_data.name}')

        project = project_repo.create_project(Project.from_schema(project_data))
        db.session.commit()
        return ProjectSchema.from_project(project).model_dump()

    @bp.route("/projects", methods=["GET"])
    @access_controller.requires_permission(general="project:read")
    def get_projects():
        return [ProjectSchema.from_project(p).model_dump() for p in project_repo.get_projects()]

    @bp.route("/projects/<slug>", methods=["GET"])
    @access_controller.requires_permission(general="project:read")
    def get_project_by_slug(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Project "{slug}" not found"')
        return ProjectSchema.from_project(project).model_dump()

    @bp.route("/projects/<slug>", methods=["PUT"])
    @access_controller.requires_permission(general="project:update", project="project:update")
    @transactional
    def update_project_by_slug(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Project "{slug}" not found')

        project_update = UpdateProjectSchema(**request.json)
        if project_update.name and project_repo.get_project_by_slug(slugify(project_update.name)) is not None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'A slug already exists for this name, please pick a new one: "{project_update.name}')

        updated_project = project_repo.update_project(project, project_update)
        return ProjectSchema.from_project(updated_project).model_dump()

    @bp.route("/projects/<slug>", methods=["DELETE"])
    @access_controller.requires_permission(general="project:delete", project="project:delete")
    @transactional
    def delete_project_by_slug(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Project "{slug}" not found')

        name = project_repo.delete_project(project)
        return {f"description": "Project deleted successfully", "name": name}

    return bp
