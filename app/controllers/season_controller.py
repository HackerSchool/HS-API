from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import abort

from app.access import AccessController
from app.models.season_model import Season
from app.repositories.season_repository import SeasonRepository
from app.schemas.season_schema import SeasonSchema
from app.schemas.update_season_schema import UpdateSeasonSchema

from app.decorators import transactional


def create_season_bp(*, season_repo: SeasonRepository, access_controller: AccessController):
    bp = Blueprint("season", __name__)

    @bp.route("/seasons", methods=["POST"])
    #@access_controller.requires_permission(general="season:create")
    @transactional
    def create_season():
        season_data = SeasonSchema(**request.json)
        if season_data.season_number and season_repo.get_season_by_number(season_data.season_number) is not None:
            return abort(HTTPStatus.CONFLICT, description=f'Season with number "{season_data.season_number}" already exists')

        season = season_repo.create_season(Season.from_schema(schema = season_data))
        return SeasonSchema.from_season(season).model_dump()

    @bp.route("/seasons", methods=["GET"])
    #@access_controller.requires_permission(general="season:read")
    def get_seasons():
        return [SeasonSchema.from_season(x).model_dump() for x in season_repo.get_seasons()]

    @bp.route("/seasons/<int:season_number>", methods=["GET"])
    #@access_controller.requires_permission(general="season:read")
    def get_season_by_number(season_number):
        if (season := season_repo.get_season_by_number(season_number=season_number)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Season with season_number "{season_number}" not found')
        return SeasonSchema.from_season(season).model_dump()

    @bp.route("/seasons/active", methods=["GET"])
    #@access_controller.requires_permission(general="season:read")
    def get_active_season():
        season = season_repo.get_active_season()
        if season is None:
            return abort(HTTPStatus.NOT_FOUND, description="No active season found")
        return SeasonSchema.from_season(season).model_dump()

    @bp.route("/seasons/range", methods=["GET"])
    #@access_controller.requires_permission(general="season:read")
    def get_seasons_in_range():
        start = request.args.get("start")
        end = request.args.get("end")

        if not start or not end:
            return abort(HTTPStatus.BAD_REQUEST, description='Query params "start" and "end" are mandatory')
        if not is_valid_datestring(start) or not is_valid_datestring(end):
            return abort(HTTPStatus.BAD_REQUEST, description='Invalid dates: use "YYYY-MM-DD"')

        seasons = season_repo.get_seasons_in_range(start, end)
        return [SeasonSchema.from_season(s).model_dump() for s in seasons]


    @bp.route("/seasons/<int:season_number>", methods=["PUT"])
    #@access_controller.requires_permission(general="season:update", allow_self_action=True)
    @transactional
    def update_season_by_season_number(season_number):
        if (season := season_repo.get_season_by_number(season_number)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Season with season_number "{season_number}" not found')

        season_update = UpdateSeasonSchema(**request.json)
        if season_update.season_number and season_repo.get_season_by_number(season_update.season_number) is not None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'Season with season_number "{season_update.season_number}" already exists')

        updated_season = season_repo.update_season(season, season_update)
        return SeasonSchema.from_season(updated_season).model_dump()

    @bp.route("/seasons/<int:season_number>", methods=["DELETE"])
    #@access_controller.requires_permission(general="season:delete", allow_self_action=True)
    @transactional
    def delete_season_by_number(season_number):
        if (season := season_repo.get_season_by_number(season_number)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Season with season_number "{season_number}" not found')

        season_number = season_repo.delete_season(season)
        return {f"description": "Season deleted successfully", "season_number": season_number}

    return bp
