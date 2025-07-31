import pytest

import bcrypt

from app import create_app
from app.models.member_model import Member

base_user = {
    "ist_id": "ist110000",
    "username": "username",
    "name": "name",
    "email": "email",
}


class InitTestCase:
    def __init__(self, *, data: dict, override=False, field=None, value=None, exc_type=None, exc_str=None):
        self.data = data
        self.override: bool = override
        self.field: str = field
        self.value: any = value
        self.exc_type: Exception = exc_type
        self.exc_str: str = exc_str

    def __repr__(self):
        fields = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

class ValidPasswordTestCase:
    def __init__(self, *, data: dict, password: str | None):
        self.data = data
        self.password = password

    def __repr__(self):
        fields = ', '.join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

# {**base_user} is similar to a deep copy but more 🌠 pythonic 🌠
valid_init_test_cases = [
    InitTestCase(data={**base_user}),
    InitTestCase(data={**base_user}, override=True, field="member_number", value=1),
    InitTestCase(data={**base_user}, override=True, field="course", value="LEIC"),
    InitTestCase(data={**base_user}, override=True, field="roles", value=["admin", "member"]),
    InitTestCase(data={**base_user}, override=True, field="roles", value=[]),
    InitTestCase(data={**base_user}, override=True, field="join_date", value="1970-01-01"),
    InitTestCase(data={**base_user}, override=True, field="exit_date", value="1970-01-01"),
    InitTestCase(data={**base_user}, override=True, field="description", value="description"),
    InitTestCase(data={**base_user}, override=True, field="extra", value="description"),

    # boundary strings lengths
    InitTestCase(data={**base_user}, override=True, field="username", value="333"),  # 3
    InitTestCase(data={**base_user}, override=True, field="username", value="a" * 32),

    InitTestCase(data={**base_user}, override=True, field="name", value="1"),
    InitTestCase(data={**base_user}, override=True, field="name", value="a" * 256),

    InitTestCase(data={**base_user}, override=True, field="email", value="1"),
    InitTestCase(data={**base_user}, override=True, field="email", value="a" * 256),

    InitTestCase(data={**base_user}, override=True, field="roles", value=["member"]),

    InitTestCase(data={**base_user}, override=True, field="course", value="1"),
    InitTestCase(data={**base_user}, override=True, field="course", value="88888888"),  # 8

    InitTestCase(data={**base_user}, override=True, field="username", value="333"),  # 3
    InitTestCase(data={**base_user}, override=True, field="username", value="a" * 32),

    InitTestCase(data={**base_user}, override=True, field="description", value=""),  # 0
    InitTestCase(data={**base_user}, override=True, field="description", value="a" * 2048),

    InitTestCase(data={**base_user}, override=True, field="extra", value=""),  # 0
    InitTestCase(data={**base_user}, override=True, field="extra", value="a" * 2048),
]

invalid_init_test_cases = [
    InitTestCase(data={**base_user}, override=True, field="ist_id", value=123, exc_type=ValueError,
                 exc_str=f'Invalid IST ID type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="ist_id", value="", exc_type=ValueError,
                 exc_str='Invalid IST ID pattern: ""'),
    InitTestCase(data={**base_user}, override=True, field="ist_id", value="ist999999999999", exc_type=ValueError,
                 exc_str='Invalid IST ID pattern: "ist999999999999"'),
    InitTestCase(data={**base_user}, override=True, field="ist_id", value="ist1abc", exc_type=ValueError,
                 exc_str='Invalid IST ID pattern: "ist1abc"'),

    InitTestCase(data={**base_user}, override=True, field="username", value=None, exc_type=ValueError,
                 exc_str=f'Invalid username type: "{type(None)}"'),
    InitTestCase(data={**base_user}, override=True, field="username", value=123, exc_type=ValueError,
                 exc_str=f'Invalid username type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="username", value="", exc_type=ValueError,
                 exc_str='Invalid username length, minimum 3 and maximum 32 characters: ""'),
    InitTestCase(data={**base_user}, override=True, field="username", value="us", exc_type=ValueError,
                 exc_str='Invalid username length, minimum 3 and maximum 32 characters: "us"'),
    InitTestCase(data={**base_user}, override=True, field="username", value="a" * 33, exc_type=ValueError,
                 exc_str=f'Invalid username length, minimum 3 and maximum 32 characters: "{"a" * 33}"'),
    InitTestCase(data={**base_user}, override=True, field="username", value="user_", exc_type=ValueError,
                 exc_str='Invalid characters in username: "user_"'),

    InitTestCase(data={**base_user}, override=True, field="password", value=123, exc_type=ValueError,
                 exc_str=f'Invalid password type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="password", value="55555", exc_type=ValueError,
                 exc_str=f'Invalid password length, minimum 6 and maximum 256 characters'),
    InitTestCase(data={**base_user}, override=True, field="password", value="a" * 257, exc_type=ValueError,
                 exc_str=f'Invalid password length, minimum 6 and maximum 256 characters'),

    InitTestCase(data={**base_user}, override=True, field="name", value=123, exc_type=ValueError,
                 exc_str=f'Invalid name type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="name", value=None, exc_type=ValueError,
                 exc_str=f'Invalid name type: "{type(None)}"'),
    InitTestCase(data={**base_user}, override=True, field="name", value="", exc_type=ValueError,
                 exc_str=f'Invalid name length, minimum 1 and maximum 256 characters: ""'),
    InitTestCase(data={**base_user}, override=True, field="name", value="a" * 257, exc_type=ValueError,
                 exc_str=f'Invalid name length, minimum 1 and maximum 256 characters: "{"a" * 257}"'),

    InitTestCase(data={**base_user}, override=True, field="email", value=123, exc_type=ValueError,
                 exc_str=f'Invalid email type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="email", value=None, exc_type=ValueError,
                 exc_str=f'Invalid email type: "{type(None)}"'),
    InitTestCase(data={**base_user}, override=True, field="email", value="", exc_type=ValueError,
                 exc_str=f'Invalid email length, minimum 1 and maximum 256 characters: ""'),
    InitTestCase(data={**base_user}, override=True, field="email", value="a" * 257, exc_type=ValueError,
                 exc_str=f'Invalid email length, minimum 1 and maximum 256 characters: "{"a" * 257}"'),

    InitTestCase(data={**base_user}, override=True, field="roles", value=123, exc_type=ValueError,
                 exc_str=f'Invalid roles type: "{type(123)}"'),

    InitTestCase(data={**base_user}, override=True, field="course", value=123, exc_type=ValueError,
                 exc_str=f'Invalid course type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="course", value="", exc_type=ValueError,
                 exc_str=f'Invalid course length, minimum 1 and maximum 8 characters: ""'),
    InitTestCase(data={**base_user}, override=True, field="course", value="aaaaaaaaa", exc_type=ValueError,
                 exc_str=f'Invalid course length, minimum 1 and maximum 8 characters: "aaaaaaaaa"'),

    InitTestCase(data={**base_user}, override=True, field="member_number", value="nr", exc_type=ValueError,
                 exc_str=f'Invalid member_number type: "{type("str")}"'),
    InitTestCase(data={**base_user}, override=True, field="member_number", value=0, exc_type=ValueError,
                 exc_str=f'Invalid member_number, expected integer greater than 0: Got {0}'),

    InitTestCase(data={**base_user}, override=True, field="join_date", value=123, exc_type=ValueError,
                 exc_str=f'Invalid join_date type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="join_date", value="abcdef", exc_type=ValueError,
                 exc_str=f'Invalid join_date format, expected "YYYY-MM-DD": "abcdef"'),

    InitTestCase(data={**base_user}, override=True, field="exit_date", value=123, exc_type=ValueError,
                 exc_str=f'Invalid exit_date type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="exit_date", value="abcdef", exc_type=ValueError,
                 exc_str=f'Invalid exit_date format, expected "YYYY-MM-DD": "abcdef"'),

    InitTestCase(data={**base_user}, override=True, field="description", value=123, exc_type=ValueError,
                 exc_str=f'Invalid description type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="description", value="a" * 2049, exc_type=ValueError,
                 exc_str=f'Invalid description length, minimum 0 and maximum 2048 characters: "{"a" * 2049}"'),

    InitTestCase(data={**base_user}, override=True, field="extra", value=123, exc_type=ValueError,
                 exc_str=f'Invalid extra type: "{type(123)}"'),
    InitTestCase(data={**base_user}, override=True, field="extra", value="a" * 2049, exc_type=ValueError,
                 exc_str=f'Invalid extra length, minimum 0 and maximum 2048 characters: "{"a" * 2049}"'),
]

valid_password_test_cases = [
    ValidPasswordTestCase(data={**base_user}, password="six666"),
    ValidPasswordTestCase(data={**base_user}, password="a" * 256),
    ValidPasswordTestCase(data={**base_user}, password="password"),
    ValidPasswordTestCase(data={**base_user}, password=None)
]

# need to initialize the app because the models are coupled with flask-sqlalchemy
app = create_app()
app.config.update({"TESTING": True})


@pytest.mark.parametrize("test_case", valid_init_test_cases)
def test_valid_init(test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    member = Member(**test_case.data)

    for k, v in test_case.data.items():
        assert getattr(member, k) == v


@pytest.mark.parametrize("test_case", invalid_init_test_cases)
def test_invalid_init(test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    with pytest.raises(test_case.exc_type) as exc_info:
        member = Member(**test_case.data)

    assert test_case.exc_str in str(exc_info.value)


@pytest.mark.parametrize("test_case", valid_password_test_cases)
def test_valid_password_property(test_case: ValidPasswordTestCase):
    test_case.data["password"] = test_case.password
    member = Member(**test_case.data)
    assert (member.password is None and test_case.password is None) or member.matches_password(test_case.password)
