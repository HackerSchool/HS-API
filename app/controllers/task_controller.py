from http import HTTPStatus
from flask import Blueprint, request, abort

from app.auth.auth_controller import AuthController
from app.schemas.task_schema import TaskSchema
from app.schemas.update_task_schema import UpdateTaskSchema

from app.repositories.task_repository import TaskRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository

from app.models.task_model import Task
from app.decorators import transactional

def create_task_bp(*, task_repo: TaskRepository, participation_repo: ProjectParticipationRepository,
                   member_repo: MemberRepository, project_repo: ProjectRepository, auth_controller: AuthController):
    bp = Blueprint("task", __name__)

    @bp.route("/tasks", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_tasks():
        return [TaskSchema.from_task(t).model_dump() for t in task_repo.get_tasks()]

    @bp.route("/tasks/<int:task_id>", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_task_by_id(task_id: int):
        if (task := task_repo.get_task_by_id(task_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Task with ID '{task_id}' not found")
        return TaskSchema.from_task(task).model_dump()

    @bp.route("/tasks/<int:task_id>", methods=["PUT"])
    @auth_controller.requires_permission(general="task:update")
    @transactional
    def update_task_by_id(task_id: int):
        if (task := task_repo.get_task_by_id(task_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Task with ID '{task_id}' not found")

        update_schema = UpdateTaskSchema(**request.json)
        updated_task = task_repo.update_task(task, update_schema)
        return TaskSchema.from_task(updated_task).model_dump()

    @bp.route("/tasks/<int:task_id>", methods=["DELETE"])
    @auth_controller.requires_permission(general="task:delete")
    @transactional
    def delete_task_by_id(task_id: int):
        if (task := task_repo.get_task_by_id(task_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Task with ID '{task_id}' not found")

        deleted_id = task_repo.delete_task(task)
        return {"description": "Task deleted successfully", "id": deleted_id}

    def _resolve_targets(*, username: str, slug: str):
        member = member_repo.get_member_by_username(username)
        if member is None:
            abort(HTTPStatus.NOT_FOUND, description=f"Member '{username}' not found")

        project = project_repo.get_project_by_slug(slug)
        if project is None:
            abort(HTTPStatus.NOT_FOUND, description=f"Project '{slug}' not found")

        participation = participation_repo.get_participation_by_project_and_member_id(project_id=project.id, member_id=member.id)
        if participation is None:
            abort(HTTPStatus.NOT_FOUND, description=f"Participation for '{username}' in '{project.name}' not found")

        return member, project, participation

    @bp.route("/projects/<slug>/tasks", methods=["POST"])
    @auth_controller.requires_permission(general="task:create")
    @transactional
    def create_task(slug):
        task_data = TaskSchema(**request.json)
        _, _, participation = _resolve_targets(username=task_data.username, slug=slug)

        task = task_repo.create_task(Task.from_schema(schema=task_data, participation=participation))
        return TaskSchema.from_task(task).model_dump()

    @bp.route("/projects/<slug>/tasks", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_project_tasks(slug):
        if (project := project_repo.get_project_by_slug(slug)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Project '{slug}' not found")

        return [
            TaskSchema.from_task(t).model_dump(exclude="project_name")
            for p in project.project_participations
            for t in p.tasks
        ]

    @bp.route("/members/<username>/tasks", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_member_tasks(username: str):
        if (member := member_repo.get_member_by_username(username)) is None:
            abort(HTTPStatus.NOT_FOUND, description=f"Member '{username}' not found")

        return [
            TaskSchema.from_task(t).model_dump(exclude="username")
            for p in member.project_participations
            for t in p.tasks
        ]

    return bp
