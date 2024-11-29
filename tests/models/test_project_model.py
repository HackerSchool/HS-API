import pytest
from app.models.project import Project


def test_create_project():
    p = Project(
        name="name",
        start_date="1970-01-01",
        state="state",
        description="description",
    )
    assert p.name == "name"
    assert p.start_date == "1970-01-01"
    assert p.state == "state"
    assert p.description == "description"


def test_invalid_name_type():
    with pytest.raises(ValueError) as e_info:
        Project(
            name=1,
            start_date="1970-01-01",
            state="state",
            description="description",
        )
    assert e_info.match("Field 'name' must be a non-empty string with max 255 characters.")


def test_invalid_name_empty():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="",
            start_date="1970-01-01",
            state="state",
            description="description",
        )
    assert e_info.match("Field 'name' must be a non-empty string with max 255 characters.")


def test_invalid_name_long():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="n" * 256,
            start_date="1970-01-01",
            state="state",
            description="description",
        )
    assert e_info.match("Field 'name' must be a non-empty string with max 255 characters.")


def test_invalid_name_non_ascii():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="nameç",
            start_date="1970-01-01",
            state="state",
            description="description",
        )
    assert e_info.match("Invalid username, only allowed characters in the ranges a-z A-Z and 0-9 and ' ' '-' '_' '~'")


def test_invalid_state_type():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="1970-01-01",
            state=1,
            description="description",
        )
    assert e_info.match("Field 'state' must be a non-empty string.")


def test_invalid_state_empty():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="1970-01-01",
            state="",
            description="description",
        )
    assert e_info.match("Field 'state' must be a non-empty string.")


def test_invalid_state_long():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="1970-01-01",
            state="s" * 33,
            description="description",
        )
    assert e_info.match("Field 'state' must be a non-empty string.")


def test_invalid_start_date_type():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date=1,
            state="state",
            description="description",
        )
    assert e_info.match("Field 'start_date' must be a non-empty string.")


def test_invalid_start_date_empty():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="",
            state="state",
            description="description",
        )
    assert e_info.match("Field 'start_date' must be a non-empty string.")


def test_invalid_start_date_format_dd_mm_yyyy():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="01-01-1970",
            state="state",
            description="description",
        )
    assert e_info.match("'start_date' must be a valid date in the format YYYY-MM-DD.")


def test_invalid_start_date_format_mm_dd_yyyy():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="01-31-1970",
            state="state",
            description="description",
        )
    assert e_info.match("'start_date' must be a valid date in the format YYYY-MM-DD.")


def test_invalid_description_type():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="1970-01-01",
            state="state",
            description=1,
        )
    assert e_info.match("Field 'description' must be a string with max 512 characters.")


def test_invalid_description_long():
    with pytest.raises(ValueError) as e_info:
        Project(
            name="name",
            start_date="1970-01-01",
            state="state",
            description="d" * 513,
        )
    assert e_info.match("Field 'description' must be a string with max 512 characters.")
