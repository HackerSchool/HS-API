import pytest
from unittest.mock import patch

from app.models.user import User


@pytest.fixture(scope="module", autouse=True)
def roles_service_mock():
    def exists_role_side_effect(scope=None, role=""):
        if role == "admin" or role == "member" or role == "role":
            return True
        elif role == "invalid role":
            return False
        else:
            raise ValueError(f"Test error! Unpatched role: {role}")

    with patch("app.services.roles.roles_service.exists_role_in_scope", return_value=True) as mock_exists_role_in_scope:
        mock_exists_role_in_scope.side_effect = exists_role_side_effect
        yield mock_exists_role_in_scope


def test_create_user(roles_service_mock):
    u = User(
        username="username",
        password="password",
        ist_id="ist100000",
        name="name",
        email="name@hackerschool.tecnico.ulisboa.pt",
        course="LEIC",
        member_number=1,
        join_date="1970-01-01",
        exit_date="1970-01-01",
        description="description",
        extra="extra",
        roles=["admin", "member"],
    )
    assert u.username == "username"
    assert u.ist_id == "ist100000"
    assert u.name == "name"
    assert u.email == "name@hackerschool.tecnico.ulisboa.pt"
    assert u.course == "LEIC"
    assert u.member_number == 1
    assert u.join_date == "1970-01-01"
    assert u.exit_date == "1970-01-01"
    assert u.description == "description"
    assert u.extra == "extra"
    assert u.roles == ["admin", "member"]
    assert roles_service_mock.call_count == 2


def test_invalid_username_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username=1,
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'username' must be a non-empty string.")


def test_invalid_username_empty():
    with pytest.raises(ValueError) as e_info:
        User(
            username="",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'username' must be a non-empty string.")


def test_invalid_username_short():
    with pytest.raises(ValueError) as e_info:
        User(
            username="a",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Invalid username, length must be between 2 to 20 characters.")


def test_invalid_username_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="a" * 21,
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Invalid username, length must be between 2 to 20 characters.")


def test_invalid_username_non_ascii():
    with pytest.raises(ValueError) as e_info:
        User(
            username="gonçalo",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Invalid username, only allowed characters in the ranges a-z A-Z and 0-9.")


def test_invalid_ist_id_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id=1,
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'ist_id' must be a valid IST student number.")


def test_invalid_ist_id_no_prefix():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="1234",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'ist_id' must be a valid IST student number.")


def test_invalid_ist_id_length_short():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'ist_id' must be a valid IST student number.")


def test_invalid_ist_id_length_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist111111111111111111111111111111111111111111111111111111",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'ist_id' must be a valid IST student number.")


def test_invalid_name_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name=1,
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'name' must be a non-empty string with max 255 characters.")


def test_invalid_name_empty():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'name' must be a non-empty string with max 255 characters.")


def test_invalid_name_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name" + 252 * "e",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'name' must be a non-empty string with max 255 characters.")


def test_invalid_email_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email=1,
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'email' must be a non-empty string with max 255 characters.")


def test_invalid_email_empty():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'email' must be a non-empty string with max 255 characters.")


def test_invalid_email_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt" + 220 * "e",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'email' must be a non-empty string with max 255 characters.")


def test_invalid_course_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course=1,
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'course' must be a non-empty string with max 8 characters.")


def test_invalid_course_empty():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'course' must be a non-empty string with max 8 characters.")


def test_invalid_course_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEICCCCCC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'course' must be a non-empty string with max 8 characters.")


def test_invalid_member_number_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number="1",
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'member_number' must be a positive integer.")


def test_invalid_member_number_negative():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=-1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'member_number' must be a positive integer.")


def test_invalid_join_date_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date=1,
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'join_date' must be a string.")


def test_invalid_join_date_format_dd_mm_yyyy():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="01-01-1970",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("'join_date' must be a valid date in the format YYYY-MM-DD.")


def test_invalid_join_date_format_mm_dd_yyyy():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="01-31-1970",
            exit_date="1970-01-01",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("'join_date' must be a valid date in the format YYYY-MM-DD.")


def test_invalid_exit_date_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date=1,
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'exit_date' must be a string.")


def test_invalid_exit_date_format_dd_mm_yyyy():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="01-01-1970",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("'exit_date' must be a valid date in the format YYYY-MM-DD.")


def test_invalid_exit_date_format_mm_dd_yyyy():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="01-31-1970",
            description="description",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("'exit_date' must be a valid date in the format YYYY-MM-DD.")


def test_invalid_description_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description=1,
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'description' must be a string with max 512 characters.")


def test_invalid_description_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="d" * 513,
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'description' must be a string with max 512 characters.")


def test_invalid_extra_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="description",
            extra=1,
            roles=["role"],
        )
    assert e_info.match("Field 'extra' must be a string with max 512 characters.")


def test_invalid_extra_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="e" * 513,
            roles=["role"],
        )
    assert e_info.match("Field 'extra' must be a string with max 512 characters.")


def test_invalid_roles_type():
    with pytest.raises(ValueError) as e_info:
        u = User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles="roles",
        )
    assert e_info.match("Field 'roles' must be a non-empty list.")


def test_invalid_roles_empty():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles=[],
        )
    assert e_info.match("Field 'roles' must be a non-empty list.")


def test_invalid_roles_invalid_role():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles=["invalid role"],
        )
    assert e_info.match("Role does not exist 'invalid role'.")


def test_invalid_roles_empty_str():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="password",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles=[""],
        )
    assert e_info.match("A role must be a non-empty string.")


def test_invalid_password_type():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password=1,
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'password' must be a non-empty string with max 255 characters.")


def test_invalid_password_empty():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="",
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'password' must be a non-empty string with max 255 characters.")


def test_invalid_password_long():
    with pytest.raises(ValueError) as e_info:
        User(
            username="username",
            password="p" * 256,
            ist_id="ist100000",
            name="name",
            email="name@hackerschool.tecnico.ulisboa.pt",
            course="LEIC",
            member_number=1,
            join_date="1970-01-01",
            exit_date="1970-01-01",
            description="ddescription",
            extra="extra",
            roles=["role"],
        )
    assert e_info.match("Field 'password' must be a non-empty string with max 255 characters.")
