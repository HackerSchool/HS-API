from http import HTTPStatus

from flask import Blueprint
from flask import abort
from flask import request

from app.auth.auth_controller import AuthController

from app.decorators import transactional

from app.models.project_participation_model import ProjectParticipation

from app.repositories.member_repository import MemberRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.project_repository import ProjectRepository

from app.schemas.project_participation_schema import ProjectParticipationSchema
from app.schemas.update_project_participation_schema import UpdateProjectParticipationSchema


def create_participation_bp(*, participation_repo: ProjectParticipationRepository, auth_controller: AuthController,
                            member_repo: MemberRepository, project_repo: ProjectRepository):
    bp = Blueprint("participation", __name__)

    @bp.route("/projects/<slug>/participations", methods=["POST"])
    @auth_controller.requires_permission(general="participation:create", project="add-participant")
    @transactional
    def create_participation(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Project '{slug}' not found")

        participation_data = ProjectParticipationSchema(**request.json)
        if (member := member_repo.get_member_by_username(participation_data.username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Member with username "{participation_data.username}" not found')

        if participation_repo.get_participation_by_project_and_member_id(project_id=project.id,
                                                                         member_id=member.id) is not None:
            return abort(HTTPStatus.CONFLICT,
                         description=f"Participation for '{participation_data.username}' in '{participation_data.project_name}' already exists")

        participation = participation_repo.create_participation(
            ProjectParticipation.from_schema(member=member, project=project, schema=participation_data)
        )
        return ProjectParticipationSchema.from_participation(participation).model_dump()

    @bp.route("/projects/<slug>/participations", methods=["GET"])
    @auth_controller.requires_permission(general="participation:read")
    def get_participations(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Project with name '{slug}' not found")
        return [ProjectParticipationSchema.from_participation(x).model_dump(exclude="project_name") for x in
                project.project_participations]

    @bp.route("/members/<username>/participations", methods=["GET"])
    @auth_controller.requires_permission(general="participation:read")
    def get_member_participations(username):
        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Member with username '{username}' not found")
        return [ProjectParticipationSchema.from_participation(x).model_dump(exclude="username") for x in
                member.project_participations]

    @bp.route("/projects/<slug>/participations/<username>", methods=["GET"])
    @auth_controller.requires_permission(general="participation:read")
    @transactional
    def get_participation_by_username(slug, username):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Project '{slug}' not found")

        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Member with username '{username}' not found")

        if (participation := participation_repo.get_participation_by_project_and_member_id(project_id=project.id,
                                                                                           member_id=member.id)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Participation for '{username}' in '{slug}' not found")

        return ProjectParticipationSchema.from_participation(participation).model_dump()

    @bp.route("/projects/<slug>/participations/<username>", methods=["PUT"])
    @auth_controller.requires_permission(general="participation:update", project="edit-participant")
    @transactional
    def update_participation_by_username(username, slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Project with name '{slug}' not found")

        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Member with username '{username}' not found")

        participation_update = UpdateProjectParticipationSchema(**request.json)
        if (participation := participation_repo.get_participation_by_project_and_member_id(project_id=project.id,
                                                                                           member_id=member.id)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Participation for '{username}' in '{slug}' not found")

        updated_participation = participation_repo.update_participation(participation=participation,
                                                                        update_values=participation_update)
        return ProjectParticipationSchema.from_participation(updated_participation).model_dump()

    @bp.route("/projects/<slug>/participations/<username>", methods=["DELETE"])
    @auth_controller.requires_permission(general="participation:delete", project="remove-participant")
    @transactional
    def delete_participation_by_username(slug, username):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Project with name '{slug}' not found")

        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Member with username '{username}' not found")

        if (participation := participation_repo.get_participation_by_project_and_member_id(project_id=project.id,
                                                                                           member_id=member.id)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f"Participation for '{username}' in '{slug}' not found")

        username, project_name = participation_repo.delete_participation(participation)
        return {f"description": "Participation deleted successfully", "username": username,
                "project_name": project_name}

    return bp
