from sqlalchemy.orm import Mapped, mapped_column

class ProjectParticipation:
    __tablename__ = "project_participation"

    join_date: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column()
