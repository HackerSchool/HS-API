import pydantic
import pytest

from app.schemas.update_member_schema import UpdateMemberSchema

def test_valid_update_member_schema():
    schema = UpdateMemberSchema(username="newusername", join_date="1970-01-01")
    assert schema.username == "newusername"
    assert schema.join_date == "1970-01-01"

def test_valid_none_date_update_member_schema():
    schema = UpdateMemberSchema(username="newusername", join_date=None)
    assert schema.username == "newusername"
    assert schema.join_date is None

def test_invalid_update_user_schema():
    with pytest.raises(ValueError) as exc_info:
        schema = UpdateMemberSchema(join_date="datestring")
    assert exc_info.type == pydantic.ValidationError
    assert "Invalid date" in str(exc_info.value.errors()[0].get("ctx", {}).get("error", None))

