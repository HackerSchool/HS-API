import pytest

from app import create_app
from app.utils import ProjectStateEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.project_participation_model import ProjectParticipation

# need to initialize the app because the models are coupled with flask-sqlalchemy
app = create_app()
app.config.update({"TESTING": True})

base_member = {
    "username": "username",
    "name": "name",
    "email": "email",
}

base_project = {
    "name": "proj_name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE
}

base_participation = {
    "join_date": "1970-01-01"
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


valid_init_test_cases = [
    InitTestCase(data={**base_participation}),
    InitTestCase(data={**base_participation}, override=True, field="roles", value=["coordinator"]),
    InitTestCase(data={**base_participation}, override=True, field="roles", value=["coordinator", "member"]),
    InitTestCase(data={**base_participation}, override=True, field="roles", value=[]),
]

invalid_init_test_cases = [
    InitTestCase(data={**base_participation}, override=True, field="join_date", value=None, exc_type=ValueError,
                 exc_str=f'Invalid join_date type: "{type(None)}"'),
    InitTestCase(data={**base_participation}, override=True, field="join_date", value=123, exc_type=ValueError,
                 exc_str=f'Invalid join_date type: "{type(123)}"'),
    InitTestCase(data={**base_participation}, override=True, field="join_date", value="join_date", exc_type=ValueError,
                 exc_str='Invalid join_date format, expected "YYYY-MM-DD": "join_date"'),

    InitTestCase(data={**base_participation}, override=True, field="roles", value=123, exc_type=ValueError,
                 exc_str=f'Invalid roles type: "{type(123)}"'),
]


@pytest.fixture
def member():
    return Member(**base_member)

@pytest.fixture
def project():
    return Project(**base_project)

@pytest.mark.parametrize("test_case", valid_init_test_cases)
def test_valid_init(member, project, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    member = ProjectParticipation(member=member, project=project, **test_case.data)

    for k, v in test_case.data.items():
        assert getattr(member, k) == v


@pytest.mark.parametrize("test_case", invalid_init_test_cases)
def test_invalid_init(member, project, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    with pytest.raises(test_case.exc_type) as exc_info:
        ProjectParticipation(member=member, project=project, **test_case.data)

    assert test_case.exc_str in str(exc_info.value)
