from http import HTTPStatus
from flask import Blueprint, request, abort

from app.access import AccessController
from app.schemas.task_schema import TaskSchema
from app.schemas.update_task_schema import UpdateTaskSchema

from app.repositories.task_repository import TaskRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository
from app.repositories.season_repository import SeasonRepository

from app.models.task_model import Task
from app.decorators import transactional


def create_task_bp(*, task_repo: TaskRepository, participation_repo: ProjectParticipationRepository, 
                    season_repo: SeasonRepository, member_repo: MemberRepository,
                    project_repo: ProjectRepository, access_controller: AccessController):
    bp = Blueprint("task", __name__)

    def _resolve_targets(username: str, project_name: str, season_number: int):
        member = member_repo.get_member_by_username(username)
        if member is None:
            abort(HTTPStatus.NOT_FOUND, description=f'Member "{username}" not found')

        project = project_repo.get_project_by_name(project_name)
        if project is None:
            abort(HTTPStatus.NOT_FOUND, description=f'Project "{project_name}" not found')

        participation = participation_repo.get_pp_by_project_and_member_id(project.id, member.id)
        if participation is None:
            abort(HTTPStatus.NOT_FOUND, description="Participation not found for this member and project")

        season = season_repo.get_season_by_number(season_number)
        if season is None:
            abort(HTTPStatus.NOT_FOUND, description=f'Season "{season_number}" not found')

        return member, project, participation, season

    @bp.route("/tasks", methods=["POST"])
    # @access_controller.requires_permission(general="task:create")
    @transactional
    def create_task():
        task_data = TaskSchema(**request.json)
        _, _, participation, season = _resolve_targets(task_data.username, task_data.project_name, task_data.season_number)

        if task_repo.get_task_by_participation_and_season(participation.id, season.id) is not None:
            return abort(HTTPStatus.CONFLICT, description="Task already exists for this participation and season")


        task = task_repo.create_task(Task.from_schema(season=season, participation=participation, schema=task_data))
        return TaskSchema.from_task(task).model_dump()

    @bp.route("/tasks/<username>/<project_name>/<int:season_number>", methods=["GET"])
    # @access_controller.requires_permission(general="task:read")
    def get_task(username: str, project_name: str, season_number: int):
        _, _, participation, season = _resolve_targets(username, project_name, season_number)
        
        task = task_repo.get_task_by_participation_and_season(participation.id, season.id)
        if task is None:
            return abort(HTTPStatus.NOT_FOUND, description="Task not found")
        return TaskSchema.from_task(task).model_dump()

    @bp.route("/tasks/<username>/<project_name>/<int:season_number>", methods=["PUT"])
    # @access_controller.requires_permission(general="task:update")
    @transactional
    def update_task(username: str, project_name: str, season_number: int):
        _, _, participation, season = _resolve_targets(username, project_name, season_number)

        task = task_repo.get_task_by_participation_and_season(participation.id, season.id)
        if task is None:
            return abort(HTTPStatus.NOT_FOUND, description="Task not found")

        update_schema = UpdateTaskSchema(**request.json)
        updated_task = task_repo.update_task(task, update_schema)
        return TaskSchema.from_task(updated_task).model_dump()

    @bp.route("/tasks/<username>/<project_name>/<int:season_number>", methods=["DELETE"])
    # @access_controller.requires_permission(general="task:delete")
    @transactional
    def delete_task(username: str, project_name: str, season_number: int):
        _, _, participation, season = _resolve_targets(username, project_name, season_number)

        task = task_repo.get_task_by_participation_and_season(participation.id, season.id)
        if task is None:
            return abort(HTTPStatus.NOT_FOUND, description="Task not found")

        deleted_id = task_repo.delete_task(task)
        return {"description": "Task deleted successfully", "id": deleted_id}

    return bp