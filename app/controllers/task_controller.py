from http import HTTPStatus
from flask import Blueprint, request, abort

from app.auth.auth_controller import AuthController
from app.schemas.task_schema import TaskSchema
from app.schemas.update_task_schema import UpdateTaskSchema
from app.schemas.team_task_schema import TeamTaskSchema
from app.schemas.update_team_task_schema import UpdateTeamTaskSchema

from app.repositories.task_repository import TaskRepository
from app.repositories.team_task_repository import TeamTaskRepository
from app.repositories.member_repository import MemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.project_participation_repository import ProjectParticipationRepository

from app.models.task_model import Task
from app.models.team_task_model import TeamTask
from app.decorators import transactional

def create_task_bp(*, task_repo: TaskRepository, team_task_repo: TeamTaskRepository,
                   participation_repo: ProjectParticipationRepository,
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

    def _resolve_project(*, slug: str):
        project = project_repo.get_project_by_slug(slug)
        if project is None:
            abort(HTTPStatus.NOT_FOUND, description=f"Project '{slug}' not found")
        return project

    def _resolve_member(*, username: str):
        member = member_repo.get_member_by_username(username)
        if member is None:
            abort(HTTPStatus.NOT_FOUND, description=f"Member '{username}' not found")
        return member

    def _resolve_targets(*, username: str, slug: str):
        """Resolve member, project, and participation. Returns None for participation if user has no project."""
        member = _resolve_member(username=username)
        
        # Special handling for "contribuicoes-individuais" - create project if it doesn't exist
        INDIVIDUAL_PROJECT_SLUG = "contribuicoes-individuais"
        if slug == INDIVIDUAL_PROJECT_SLUG:
            project = _get_or_create_individual_project()
        else:
            project = _resolve_project(slug=slug)
        
        participation = participation_repo.get_participation_by_project_and_member_id(project_id=project.id, member_id=member.id)
        return member, project, participation

    def _get_or_create_individual_project():
        """Get or create the 'Contribuições Individuais' project for users without teams"""
        INDIVIDUAL_PROJECT_NAME = "Contribuições Individuais"
        INDIVIDUAL_PROJECT_SLUG = "contribuicoes-individuais"
        
        project = project_repo.get_project_by_slug(INDIVIDUAL_PROJECT_SLUG)
        if project is None:
            # Create the project if it doesn't exist
            from app.models.project_model import Project
            from app.utils import ProjectStateEnum
            from datetime import date
            
            project = Project(
                name=INDIVIDUAL_PROJECT_NAME,
                state=ProjectStateEnum.ACTIVE,
                start_date=date.today().isoformat(),
                description="Projeto especial para contribuições individuais de membros sem equipa atribuída"
            )
            project_repo.create_project(project)
            # Flush to get the ID
            from app.extensions import db
            db.session.flush()
        
        return project

    def _get_or_create_individual_participation(member):
        """Get or create participation in 'Contribuições Individuais' for a member"""
        project = _get_or_create_individual_project()
        
        # Check if participation already exists
        participation = participation_repo.get_participation_by_project_and_member_id(
            project_id=project.id, 
            member_id=member.id
        )
        
        if participation is None:
            # Create participation automatically
            from app.models.project_participation_model import ProjectParticipation
            from datetime import date
            
            participation = ProjectParticipation(
                member=member,
                project=project,
                roles=["member"],
                join_date=date.today().isoformat()
            )
            participation_repo.create_participation(participation)
            # Flush to ensure it's available
            from app.extensions import db
            db.session.flush()
        
        return participation

    @bp.route("/projects/<slug>/tasks", methods=["POST"])
    @auth_controller.requires_permission(general="task:create")
    @transactional
    def create_task(slug):
        """Create a task for a specific project"""
        task_data = TaskSchema(**request.json)
        # Resolve member first (always needed)
        member = _resolve_member(username=task_data.username)
        
        # Try to find participation
        _, _, participation = _resolve_targets(username=task_data.username, slug=slug)
        
        # If participation is None, create one in "Contribuições Individuais"
        if participation is None:
            participation = _get_or_create_individual_participation(member)

        task = task_repo.create_task(Task.from_schema(
            schema=task_data, 
            participation=participation
        ))
        return TaskSchema.from_task(task).model_dump()

    @bp.route("/projects/<slug>/tasks", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_project_tasks(slug):
        project = _resolve_project(slug=slug)

        return [
            TaskSchema.from_task(t).model_dump(exclude="project_name")
            for p in project.project_participations
            for t in p.tasks
        ]

    @bp.route("/projects/<slug>/team-tasks", methods=["POST"])
    @auth_controller.requires_permission(general="task:create")
    @transactional
    def create_team_task(slug):
        task_data = TeamTaskSchema(**request.json)
        project = _resolve_project(slug=slug)

        task = team_task_repo.create_task(TeamTask.from_schema(schema=task_data, project=project))
        return TeamTaskSchema.from_task(task).model_dump()

    @bp.route("/projects/<slug>/team-tasks", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_project_team_tasks(slug):
        project = _resolve_project(slug=slug)

        return [
            TeamTaskSchema.from_task(t).model_dump(exclude="project_name")
            for t in project.team_tasks
        ]

    @bp.route("/team-tasks/<int:task_id>", methods=["GET"])
    @auth_controller.requires_permission(general="task:read")
    def get_team_task_by_id(task_id: int):
        if (task := team_task_repo.get_task_by_id(task_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Team task with ID '{task_id}' not found")
        return TeamTaskSchema.from_task(task).model_dump()

    @bp.route("/team-tasks/<int:task_id>", methods=["PUT"])
    @auth_controller.requires_permission(general="task:update")
    @transactional
    def update_team_task_by_id(task_id: int):
        if (task := team_task_repo.get_task_by_id(task_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Team task with ID '{task_id}' not found")

        update_schema = UpdateTeamTaskSchema(**request.json)
        updated_task = team_task_repo.update_task(task, update_schema)
        return TeamTaskSchema.from_task(updated_task).model_dump()

    @bp.route("/team-tasks/<int:task_id>", methods=["DELETE"])
    @auth_controller.requires_permission(general="task:delete")
    @transactional
    def delete_team_task_by_id(task_id: int):
        if (task := team_task_repo.get_task_by_id(task_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f"Team task with ID '{task_id}' not found")

        deleted_id = team_task_repo.delete_task(task)
        return {"description": "Team task deleted successfully", "id": deleted_id}

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
