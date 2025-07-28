from http import HTTPStatus

from flask import Blueprint
from flask import request
from flask import abort

from app.schemas.member_schema import MemberSchema
from app.schemas.update_member_schema import UpdateMemberSchema

from app.repositories.member_repository import MemberRepository

from app.models.member_model import Member


def create_member_bp(*, member_repo: MemberRepository):
    bp = Blueprint("member", __name__)

    @bp.route("/members", methods=["POST"])
    def create_member():
        member_data = MemberSchema(**request.json)
        if member_data.ist_id and member_repo.get_member_by_ist_id(member_data.ist_id) is not None:
            return abort(HTTPStatus.CONFLICT, description=f'Member with IST ID "{member_data.ist_id}" already exists')
        if member_repo.get_member_by_username(member_data.username) is not None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'Member with username "{member_data.username}" already exists')
        member = member_repo.create_member(Member.from_schema(member_data))
        return MemberSchema.from_member(member).model_dump()

    @bp.route("/members", methods=["GET"])
    def get_members():
        return [MemberSchema.from_member(x).model_dump() for x in member_repo.get_members()]

    @bp.route("/members/<username>", methods=["GET"])
    def get_member_by_username(username):
        if (member := member_repo.get_member_by_username(username=username)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Member with username "{username}" not found')
        return MemberSchema.from_member(member).model_dump()

    @bp.route("/members/<username>", methods=["PUT"])
    def update_member_by_username(username):
        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Member with username "{username}" not found')

        member_update = UpdateMemberSchema(**request.json)
        if member_update.username and member_repo.get_member_by_username(member_update.username) is not None:
            return abort(HTTPStatus.CONFLICT,
                         description=f'Member with username "{member_update.username}" already exists')

        updated_member = member_repo.update_member(member, member_update)
        return MemberSchema.from_member(updated_member).model_dump()

    @bp.route("/members/<username>", methods=["DELETE"])
    def delete_member_by_username(username):
        if (member := member_repo.get_member_by_username(username)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Member with username "{username}" not found')

        username = member_repo.delete_member(member)
        return {f"description": "Member deleted successfully", "username": username}

    return bp
