from app.models.season_model import Season
from app.schemas.update_season_schema import UpdateSeasonSchema

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete, update

from typing import List
from datetime import date


class SeasonRepository:
    def __init__(self, *, db: SQLAlchemy):
        self.db = db

    def create_season(self, season: Season) -> Season:
        self.db.session.add(season)
        return season

    def get_seasons(self) -> List[Season]:
        return self.db.session.execute(select(Season)).scalars().fetchall()

    def get_season_by_id(self, id: int) -> Season | None:
        return self.db.session.execute(select(Season).where(Season.id == id)).scalars().one_or_none()

    def get_season_by_number(self, season_number: int) -> Season | None:
        return self.db.session.execute(select(Season).where(Season.season_number == season_number)).scalars().one_or_none()

    def get_active_season(self) -> Season | None:
        today = date.today().isoformat()
        return self.db.session.execute(
            select(Season).where(
                Season.start_date <= today, 
                Season.end_date >= today
            )
        ).scalars().one_or_none()

    def get_seasons_in_range(self, start: str, end: str) -> List[Season]:
        return self.db.session.execute(
            select(Season).where(
                Season.start_date >= start, 
                Season.end_date <= end
            )
        ).scalars().fetchall()

    def update_season(self, season: Season, update_values: UpdateSeasonSchema) -> Season:
        for k, v in update_values.model_dump(exclude_unset=True).items():
            setattr(season, k, v)
        return season

    def delete_season(self, season: Season) -> int:
        self.db.session.execute(delete(Season).where(Season.id == season.id))
        return season.id

