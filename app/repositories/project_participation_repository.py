from typing import Tuple, List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete, and_

from app.models.project_participation_model import ProjectParticipation
from app.schemas.update_project_participation_schema import UpdateProjectParticipationSchema


class ProjectParticipationRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_participation(self, participation: ProjectParticipation) -> ProjectParticipation:
        self.db.session.add(participation)
        return participation

    def get_participations(self) -> List[ProjectParticipation]:
        return self.db.session.execute(select(ProjectParticipation)).scalars().fetchall()

    def get_participation_by_project_and_member_id(self, *, project_id: int, member_id: int) -> Optional[ProjectParticipation]:
        return self.db.session.execute(
            select(ProjectParticipation).where(
                (ProjectParticipation.project_id == project_id) &
                (ProjectParticipation.member_id == member_id)
            )
        ).scalars().one_or_none()
        
    def update_participation(self, *, participation: ProjectParticipation, update_values: UpdateProjectParticipationSchema) -> ProjectParticipation:
        for k, v in update_values.model_dump(exclude_unset=True).items():
            setattr(participation, k, v)
        return participation

    def delete_participation(self, participation: ProjectParticipation) -> Tuple[str, str]:
        self.db.session.delete(participation)
        return participation.member.username, participation.project.name
