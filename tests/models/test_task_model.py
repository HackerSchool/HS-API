import pytest

from app import create_app
from app.utils import ProjectStateEnum, PointTypeEnum

from app.models.member_model import Member
from app.models.project_model import Project
from app.models.season_model import Season
from app.models.project_participation_model import ProjectParticipation
from app.models.task_model import Task


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
    "join_date": "1970-01-01",
}

base_season = {
    "season_number": 1,
    "start_date": "1970-01-01",
    "end_date": "1970-12-31",
}

base_task = {
    "point_type": PointTypeEnum.PJ,
    "points": 1,
    "description": "description"
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
    InitTestCase(data={**base_task}, override=False),
    InitTestCase(data={**base_task}, override=True, field="points", value=None),
    InitTestCase(data={**base_task}, override=True, field="description", value=None),
    InitTestCase(data={**base_task}, override=True, field="description", value=""),
    InitTestCase(data={**base_task}, override=True, field="description", value="a" * 2048),
    InitTestCase(data={**base_task}, override=True, field="finished_at", value=None),
    InitTestCase(data={**base_task}, override=True, field="finished_at", value="1970-01-01"),
]

invalid_init_test_cases = [
    # point_type
    InitTestCase(data={**base_task}, override=True, field="point_type", value=None,
                 exc_type=ValueError, exc_str=f'Invalid point_typee: "{type(None)}"'),
    InitTestCase(data={**base_task}, override=True, field="point_type", value=123,
                 exc_type=ValueError, exc_str=f'Invalid point_typee: "{type(123)}"'),
    InitTestCase(data={**base_task}, override=True, field="point_type", value="x",
                 exc_type=ValueError, exc_str=f'Invalid point_typee: "{type("x")}"'),

    # points
    InitTestCase(data={**base_task}, override=True, field="points", value="1",
                 exc_type=ValueError, exc_str=f'Invalid points type: "{type("1")}"'),
    InitTestCase(data={**base_task}, override=True, field="points", value=0,
                 exc_type=ValueError, exc_str="Invalid points, expected integer greater than 0: Got 0"),
    InitTestCase(data={**base_task}, override=True, field="points", value=-5,
                 exc_type=ValueError, exc_str="Invalid points, expected integer greater than 0: Got -5"),

    # finished_at
    InitTestCase(data={**base_task}, override=True, field="finished_at", value=123,
                 exc_type=ValueError, exc_str=f'Invalid finished_at type: "{type(123)}"'),
    InitTestCase(data={**base_task}, override=True, field="finished_at", value="bad",
                 exc_type=ValueError, exc_str='Invalid finished_at format, expected "YYYY-MM-DD": "bad"'),

    # description
    InitTestCase(data={**base_task}, override=True, field="description", value=123,
                 exc_type=ValueError, exc_str=f'Invalid description type: "{type(123)}"'),
    InitTestCase(data={**base_task}, override=True, field="description", value="a" * 2049,
                 exc_type=ValueError, exc_str=f'Invalid description length, minimum 0 and maximum 2048 characters: "{"a" * 2049}"'),
]


@pytest.fixture
def member():
    return Member(**base_member)


@pytest.fixture
def project():
    return Project(**base_project)


@pytest.fixture
def participation(member, project):
    return ProjectParticipation(member=member, project=project, **base_participation)


@pytest.fixture
def season():
    return Season(**base_season)


@pytest.mark.parametrize("test_case", valid_init_test_cases)
def test_valid_init(season, participation, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    task = Task(season=season, participation=participation, **test_case.data)

    for k, v in test_case.data.items():
        assert getattr(task, k) == v


@pytest.mark.parametrize("test_case", invalid_init_test_cases)
def test_invalid_init(season, participation, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    with pytest.raises(test_case.exc_type) as exc_info:
        Task(season=season, participation=participation, **test_case.data)

    assert test_case.exc_str in str(exc_info.value)
