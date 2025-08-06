from app.models.project_participation_model import ProjectParticipation
from app.schemas.update_project_participation_schema import UpdateProjectParticipationSchema

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete, update

from typing import List

class ProjectParticipationRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_pp(self, pp: ProjectParticipation) -> ProjectParticipation:
        self.db.session.add(pp)
        return pp

    def get_pps(self) -> List[ProjectParticipation]:
        return self.db.session.execute(select(ProjectParticipation)).scalars().fetchall()

    def get_pp_by_id(self, id: int) -> ProjectParticipation | None:
        return self.db.session.execute(select(ProjectParticipation).where(ProjectParticipation.id == id)).scalars().one_or_none()

    def get_pp_by_project_and_member_id(self, project_id: int, member_id: int) -> ProjectParticipation | None:
        return self.db.session.execute(
            select(ProjectParticipation).where(
                ProjectParticipation.project_id == project_id,
                ProjectParticipation.member_id == member_id
            )
        ).scalars().one_or_none()
        
    def update_pp_by_id(self, pp: ProjectParticipation, update_values: UpdateProjectParticipationSchema) -> ProjectParticipation:
        for k, v in update_values.model_dump(exclude_unset=True).items():
            setattr(pp, k, v)
        return pp

    def delete_pp_by_project_and_member_id(self, pp: ProjectParticipation) -> int:
        self.db.session.execute(delete(ProjectParticipation).where(ProjectParticipation.id == pp.id))
        return pp.id
