import pydantic
import pytest

from app.schemas.member_schema import MemberSchema

base_member = {
    "ist_id": "ist100000",
    "name": "name",
    "username": "username",
    "email": "email",
}

def test_valid_datestring():
    data = {**base_member}
    data["join_date"] = "1970-01-01"

    schema = MemberSchema(**data)
    assert schema.ist_id == data["ist_id"]
    assert schema.username == data["username"]
    assert schema.name == base_member["name"]
    assert schema.email == base_member["email"]
    assert schema.join_date == data["join_date"]

def test_invalid_datestring():
    data = {**base_member}
    data["join_date"] = "date"
    with pytest.raises(ValueError) as exc_info:
        schema = MemberSchema(**data)

    assert exc_info.type == pydantic.ValidationError
    assert "Invalid date" in str(exc_info.value.errors()[0].get("ctx", {}).get("error", None))
