from http import HTTPStatus
from unittest.mock import MagicMock
import pytest

from flask.testing import FlaskClient

from app import create_app
from app.models.season_model import Season
from app.schemas.season_schema import SeasonSchema
from app.schemas.update_season_schema import UpdateSeasonSchema
from app.repositories.season_repository import SeasonRepository


base_season = {
    "season_number": 1,
    "start_date": "1970-01-01",
    "end_date": "1970-12-31",
}


@pytest.fixture
def mock_season_repo():
    return MagicMock()


@pytest.fixture
def client(mock_season_repo):
    from app.config import Config
    Config.ENABLED_ACCESS_CONTROL = False

    app = create_app(season_repo=mock_season_repo)
    with app.test_client() as client:
        yield client


def test_create_season(client: FlaskClient, mock_season_repo: SeasonRepository):
    season = Season(**base_season)
    schema = SeasonSchema.from_season(season)

    mock_season_repo.get_season_by_number.return_value = None
    mock_season_repo.create_season.return_value = season

    rsp = client.post("/seasons", json=schema.model_dump())
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in base_season.items():
        assert rsp.json[k] == v


def test_create_season_conflict(client: FlaskClient, mock_season_repo: SeasonRepository):
    season = Season(**base_season)
    schema = SeasonSchema.from_season(season)

    mock_season_repo.get_season_by_number.return_value = not None
    rsp = client.post("/seasons", json=schema.model_dump())
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_get_seasons_empty(client: FlaskClient, mock_season_repo: SeasonRepository):
    mock_season_repo.get_seasons.return_value = []
    rsp = client.get("/seasons")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json == []


def test_get_seasons(client: FlaskClient, mock_season_repo: SeasonRepository):
    s1 = Season(**base_season)
    s2 = Season(season_number=2, start_date="1971-01-01", end_date="1971-12-31")
    s3 = Season(season_number=3, start_date="1972-01-01", end_date="1972-12-31")

    mock_season_repo.get_seasons.return_value = [s1, s2, s3]
    rsp = client.get("/seasons")

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert isinstance(rsp.json, list)
    assert len(rsp.json) == 3
    assert {o["season_number"] for o in rsp.json} == {1, 2, 3}


def test_get_season_by_number(client: FlaskClient, mock_season_repo: SeasonRepository):
    season = Season(**base_season)
    mock_season_repo.get_season_by_number.return_value = season

    rsp = client.get(f'/seasons/{base_season["season_number"]}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in base_season.items():
        assert rsp.json[k] == v


def test_get_season_by_number_not_found(client: FlaskClient, mock_season_repo: SeasonRepository):
    mock_season_repo.get_season_by_number.return_value = None
    rsp = client.get(f'/seasons/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_get_active_season(client: FlaskClient, mock_season_repo: SeasonRepository):
    season = Season(**base_season)
    mock_season_repo.get_active_season.return_value = season

    rsp = client.get("/seasons/active")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    for k, v in base_season.items():
        assert rsp.json[k] == v


def test_get_active_season_not_found(client: FlaskClient, mock_season_repo: SeasonRepository):
    mock_season_repo.get_active_season.return_value = None
    rsp = client.get("/seasons/active")
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_get_seasons_in_range_missing_params(client: FlaskClient):
    rsp = client.get("/seasons/range")
    assert rsp.status_code == HTTPStatus.BAD_REQUEST
    assert rsp.mimetype == "application/json"


def test_get_seasons_in_range_invalid_dates(client: FlaskClient):
    rsp = client.get("/seasons/range?start=bad&end=also-bad")
    assert rsp.status_code == HTTPStatus.BAD_REQUEST
    assert rsp.mimetype == "application/json"


def test_get_seasons_in_range_ok(client: FlaskClient, mock_season_repo: SeasonRepository):
    s1 = Season(**base_season)
    s2 = Season(season_number=2, start_date="1971-01-01", end_date="1971-12-31")
    mock_season_repo.get_seasons_in_range.return_value = [s1, s2]

    rsp = client.get("/seasons/range?start=1970-01-01&end=1971-12-31")
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert [o["season_number"] for o in rsp.json] == [1, 2]


def test_update_season_not_found(client: FlaskClient, mock_season_repo: SeasonRepository):
    mock_season_repo.get_season_by_number.return_value = None
    rsp = client.put(f'/seasons/{base_season["season_number"]}', json={"start_date": "1980-01-01"})
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_update_season_conflict_number(client: FlaskClient, mock_season_repo: SeasonRepository):
    mock_season_repo.get_season_by_number.side_effect = [Season(**base_season), object()]

    rsp = client.put(f'/seasons/{base_season["season_number"]}', json={"season_number": 99})
    assert rsp.status_code == HTTPStatus.CONFLICT
    assert rsp.mimetype == "application/json"


def test_update_season_ok(client: FlaskClient, mock_season_repo: SeasonRepository):
    current = Season(**base_season)
    updated = Season(season_number=2, start_date="1980-01-01", end_date="1980-12-31")

    mock_season_repo.get_season_by_number.side_effect = [current, None]
    mock_season_repo.update_season.return_value = updated

    payload = UpdateSeasonSchema(season_number=2, start_date="1980-01-01", end_date="1980-12-31").model_dump()
    rsp = client.put(f'/seasons/{base_season["season_number"]}', json=payload)

    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["season_number"] == 2
    assert rsp.json["start_date"] == "1980-01-01"
    assert rsp.json["end_date"] == "1980-12-31"


def test_delete_season_not_found(client: FlaskClient, mock_season_repo: SeasonRepository):
    mock_season_repo.get_season_by_number.return_value = None
    rsp = client.delete(f'/seasons/{base_season["season_number"]}')
    assert rsp.status_code == HTTPStatus.NOT_FOUND
    assert rsp.mimetype == "application/json"


def test_delete_season_ok(client: FlaskClient, mock_season_repo: SeasonRepository):
    s = Season(**base_season)
    mock_season_repo.get_season_by_number.return_value = s
    mock_season_repo.delete_season.return_value = s.season_number

    rsp = client.delete(f'/seasons/{base_season["season_number"]}')
    assert rsp.status_code == 200
    assert rsp.mimetype == "application/json"
    assert rsp.json["season_number"] == base_season["season_number"]
    assert "description" in rsp.json
