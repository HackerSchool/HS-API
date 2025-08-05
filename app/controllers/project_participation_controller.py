from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import abort

from app.access import AccessController
from app.schemas.project_participation_schema import ProjectParticipationSchema
from app.schemas.update_project_participation_schema import UpdateProjectParticipationSchema

from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository

from app.models.project_participation_model import ProjectParticipation
from app.decorators import transactional

def create_pp_bp(*, pp_repo: ProjectParticipationRepository, 
                access_controller: AccessController, member_repo: MemberRepository,
                project_repo: ProjectRepository):
    bp = Blueprint("project_participation", __name__)

    @bp.route("/project_participations", methods=["POST"])
    #@access_controller.requires_permission(general="project_participation:create", project="project:update")
    @transactional
    def create_pp():
        pp_data = ProjectParticipationSchema(**request.json)
        if (project := project_repo.get_project_by_name(pp_data.project_name)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Project with name "{pp_data.project_name}" not found')

        if (member := member_repo.get_member_by_username(pp_data.username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Member with username "{pp_data.username}" not found')

        if pp_repo.get_pp_by_project_and_member_id(project_id=project.id, member_id=member.id) is not None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'ProjectParticipation already exists')
                         
        pp = pp_repo.create_pp(ProjectParticipation(member = member, project = project))
        return ProjectParticipationSchema.from_pp(pp).model_dump()

    @bp.route("/project_participations", methods=["GET"])
    #@access_controller.requires_permission(general="project_participation:read")
    def get_pps():
        return [ProjectParticipationSchema.from_pp(x).model_dump() for x in pp_repo.get_pps()]

    @bp.route("/project_participations/<username>/<project_name>", methods=["PUT"])
    #@access_controller.requires_permission(general="project_participation:update", allow_self_action=True)
    @transactional
    def update_pp_by_username_and_project_name(username, project_name):
        if (project := project_repo.get_project_by_name(project_name)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Project with name "{project_name}" not found')

        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Member with username "{username}" not found')

        pp_update = UpdateProjectParticipationSchema(**request.json)

        if (pp := pp_repo.get_pp_by_project_and_member_id(project_id=project.id, member_id=member.id)) is None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'ProjectParticipation does not exist')
                         
        updated_pp = pp_repo.update_pp_by_id(pp, pp_update)
        return ProjectParticipationSchema.from_pp(updated_pp).model_dump()

    @bp.route("/project_participations/<username>/<project_name>", methods=["DELETE"])
    #@access_controller.requires_permission(general="project_participation:delete", allow_self_action=True)
    @transactional
    def delete_pp_by_username_and_project_name(username, project_name):

        if (project := project_repo.get_project_by_name(project_name)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Project with name "{project_name}" not found')

        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND,
                         description=f'Member with username "{username}" not found')

        if (pp := pp_repo.get_pp_by_project_and_member_id(project_id=project.id, member_id=member.id)) is None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'ProjectParticipation does not exist')

        id = pp_repo.delete_pp_by_project_and_member_id(pp)
        return {f"description": "ProjectParticipation deleted successfully", "id": id}

    return bp
