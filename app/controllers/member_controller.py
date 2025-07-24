from flask import Blueprint, request, abort
from http import HTTPStatus

from app.schemas.member_schema import MemberSchema
from app.schemas.update_member_schema import UpdateMemberSchema
from app.repositories.member_repository import MemberRepository
from app.models.member_model import Member


def create_member_bp(*, member_repo: MemberRepository):
    bp = Blueprint("member", __name__)

    @bp.route("/members", methods=["POST"])
    def create_member():
        member_data = MemberSchema(**request.json)
        if member_repo.get_member_by_ist_id(member_data.ist_id) is not None:
            return abort(HTTPStatus.CONFLICT, description=f'Member with IST ID "{member_data.ist_id}" already exists')
        if member_repo.get_member_by_username(member_data.username) is not None:
            return abort(HTTPStatus.CONFLICT, description=f'Member with username "{member_data.username}" already exists')
        member = member_repo.create_member(Member.from_schema(member_data))
        return MemberSchema.from_member(member).model_dump()

    @bp.route("/members", methods=["GET"])
    def get_members():
        return [MemberSchema.from_member(x).model_dump() for x in member_repo.get_members()]

    @bp.route("/members/<ist_id>", methods=["GET"])
    def get_member_by_ist_id(ist_id):
        if (member := member_repo.get_member_by_ist_id(ist_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Member with IST ID "{ist_id}" not found')
        return MemberSchema.from_member(member).model_dump()

    @bp.route("/members/<ist_id>", methods=["PUT"])
    def update_member_by_ist_id(ist_id):
        if (member_repo.get_member_by_ist_id(ist_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Member with IST ID "{ist_id}" not found')
        member_update = UpdateMemberSchema(**request.json)
        if member_repo.get_member_by_username(member_update.username) is not None:
            return abort(HTTPStatus.CONFLICT, description=f'Member with username "{member_update.username}" already exists')
        member_repo.update_member_by_ist_id(ist_id, **{k: v for k, v in member_update.model_dump().items() if v is not None})
        return MemberSchema.from_member(member_repo.get_member_by_ist_id(ist_id)).model_dump()

    @bp.route("/members/<ist_id>", methods=["DELETE"])
    def delete_member_by_ist_id(ist_id):
        if (member_repo.get_member_by_ist_id(ist_id)) is None:
            return abort(HTTPStatus.NOT_FOUND, description=f'Member with IST ID "{ist_id}" not found')
        member_repo.delete_member_by_ist_id(ist_id)
        return {f"description": "Deleted member sucessfully", "ist_id": ist_id}

    return bp






