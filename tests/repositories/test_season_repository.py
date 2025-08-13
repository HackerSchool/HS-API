import pytest
from datetime import date, timedelta

from sqlalchemy import select

from app import create_app
from app.config import Config
from app.extensions import db

from app.models.season_model import Season
from app.schemas.update_season_schema import UpdateSeasonSchema
from app.repositories.season_repository import SeasonRepository


base_season = {
    "season_number": 1,
    "start_date": "1970-01-01",
    "end_date": "1970-12-31",
}


@pytest.fixture(scope="function")
def app():
    Config.DATABASE_PATH = "sqlite:///:memory:"
    app = create_app()
    with app.app_context():
        db.create_all()
        yield
        db.session.commit()
        db.drop_all()


@pytest.fixture
def season_repo():
    return SeasonRepository(db=db)


def test_create_season(app, season_repo: SeasonRepository):
    season = Season(**base_season)
    season_repo.create_season(season)

    gotten_season = db.session.execute(select(Season).where(Season.season_number == base_season["season_number"])) \
        .scalars().one_or_none()
    assert gotten_season is not None
    assert gotten_season.season_number == base_season["season_number"]
    assert gotten_season.start_date == base_season["start_date"]
    assert gotten_season.end_date == base_season["end_date"]


def test_get_season_by_id(app, season_repo: SeasonRepository):
    season = Season(**base_season)
    db.session.add(season)
    db.session.flush()

    gotten_season = season_repo.get_season_by_id(season.id)
    assert gotten_season is not None
    assert gotten_season.id == season.id
    assert gotten_season.season_number == season.season_number


def test_get_season_by_number(app, season_repo: SeasonRepository):
    season = Season(**base_season)
    db.session.add(season)

    gotten_season = season_repo.get_season_by_number(season.season_number)
    assert gotten_season is not None
    assert gotten_season.season_number == season.season_number
    assert gotten_season.start_date == season.start_date
    assert gotten_season.end_date == season.end_date


def test_get_no_season_by_id(app, season_repo: SeasonRepository):
    assert season_repo.get_season_by_id(9999) is None


def test_get_no_season_by_number(app, season_repo: SeasonRepository):
    assert season_repo.get_season_by_number(9999) is None


def test_get_seasons(app, season_repo: SeasonRepository):
    seasons = set()
    for i in range(3):
        season = Season(season_number=i + 1, start_date=f"1970-01-0{i+1}", end_date=f"1970-12-2{i+1}")
        db.session.add(season)
        seasons.add(season)

    gotten_seasons = season_repo.get_seasons()
    assert {season.season_number for season in seasons} == {gs.season_number for gs in gotten_seasons}


def test_get_active_season(app, season_repo: SeasonRepository):
    # one past, one future, one active today
    today = date.today()
    active = Season(
        season_number=100,
        start_date=(today - timedelta(days=10)).isoformat(),
        end_date=(today + timedelta(days=10)).isoformat(),
    )
    past = Season(
        season_number=101,
        start_date=(today - timedelta(days=30)).isoformat(),
        end_date=(today - timedelta(days=20)).isoformat(),
    )
    future = Season(
        season_number=102,
        start_date=(today + timedelta(days=20)).isoformat(),
        end_date=(today + timedelta(days=30)).isoformat(),
    )
    db.session.add_all([past, future, active])

    gotten_season = season_repo.get_active_season()
    assert gotten_season is not None
    assert gotten_season.season_number == active.season_number


def test_get_seasons_in_range(app, season_repo: SeasonRepository):
    s1 = Season(season_number=1, start_date="1970-01-01", end_date="1970-06-30")
    s2 = Season(season_number=2, start_date="1970-07-01", end_date="1970-12-31")
    s3 = Season(season_number=3, start_date="1971-01-01", end_date="1971-12-31")
    db.session.add_all([s1, s2, s3])

    gotten_seasons = season_repo.get_seasons_in_range(start="1970-01-01", end="1970-12-31")
    nums = {g.season_number for g in gotten_seasons}
    assert nums == {1, 2}


def test_update_season(app, season_repo: SeasonRepository):
    season = Season(**base_season)
    db.session.add(season)
    db.session.flush()

    new_data = {
        "season_number": 2,
        "start_date": "1980-01-01",
        "end_date": "1980-12-31",
    }
    update_values = UpdateSeasonSchema(**new_data)

    updated = season_repo.update_season(season, update_values)
    gotten_season = db.session.execute(select(Season).where(Season.id == season.id)).scalars().one_or_none()
    assert gotten_season is not None
    assert gotten_season.season_number == updated.season_number == 2
    assert gotten_season.start_date == updated.start_date == "1980-01-01"
    assert gotten_season.end_date == updated.end_date == "1980-12-31"


def test_delete_season(app, season_repo: SeasonRepository):
    season = Season(**base_season)
    db.session.add(season)
    db.session.flush()

    deleted_id = season_repo.delete_season(season)
    assert deleted_id == season.id
    assert db.session.execute(select(Season).where(Season.id == season.id)).scalars().one_or_none() is None
