import pytest

from app import create_app
from app.utils import PointTypeEnum, ProjectStateEnum

from app.models.project_model import Project
from app.models.team_task_model import TeamTask

# initialize app for model binding
app = create_app()
app.config.update({"TESTING": True})

base_project = {
    "name": "proj_name",
    "start_date": "1970-01-01",
    "state": ProjectStateEnum.ACTIVE,
}

base_team_task = {
    "point_type": PointTypeEnum.PJ,
    "points": 5,
    "description": "team task",
    "contributors": ["user1", "user2"],
}


class InitTestCase:
    def __init__(self, *, data: dict, override=False, field=None, value=None, exc_type=None, exc_str=None):
        self.data = data
        self.override = override
        self.field = field
        self.value = value
        self.exc_type = exc_type
        self.exc_str = exc_str

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


valid_init_test_cases = [
    InitTestCase(data={**base_team_task}, override=False),
    InitTestCase(data={**base_team_task}, override=True, field="points", value=None),
    InitTestCase(data={**base_team_task}, override=True, field="points", value=-15),
    InitTestCase(data={**base_team_task}, override=True, field="description", value=None),
    InitTestCase(data={**base_team_task}, override=True, field="description", value=""),
    InitTestCase(data={**base_team_task}, override=True, field="description", value="a" * 2048),
    InitTestCase(data={**base_team_task}, override=True, field="finished_at", value=None),
    InitTestCase(data={**base_team_task}, override=True, field="finished_at", value="1970-01-01"),
    InitTestCase(data={**base_team_task}, override=True, field="contributors", value=[]),
    InitTestCase(data={**base_team_task}, override=True, field="contributors", value=["solo"]),
]

invalid_init_test_cases = [
    InitTestCase(data={**base_team_task}, override=True, field="point_type", value=None,
                 exc_type=ValueError, exc_str=f'Invalid point_typee: "{type(None)}"'),
    InitTestCase(data={**base_team_task}, override=True, field="point_type", value="x",
                 exc_type=ValueError, exc_str=f'Invalid point_typee: "{type("x")}"'),
    InitTestCase(data={**base_team_task}, override=True, field="points", value="5",
                 exc_type=ValueError, exc_str=f'Invalid points type: "{type("5")}"'),
    InitTestCase(data={**base_team_task}, override=True, field="points", value=0,
                 exc_type=ValueError, exc_str="Invalid points, expected non-zero integer: Got 0"),
    InitTestCase(data={**base_team_task}, override=True, field="finished_at", value=123,
                 exc_type=ValueError, exc_str=f'Invalid finished_at type: "{type(123)}"'),
    InitTestCase(data={**base_team_task}, override=True, field="finished_at", value="bad",
                 exc_type=ValueError, exc_str='Invalid finished_at format, expected "YYYY-MM-DD": "bad"'),
    InitTestCase(data={**base_team_task}, override=True, field="description", value=123,
                 exc_type=ValueError, exc_str=f'Invalid description type: "{type(123)}"'),
    InitTestCase(data={**base_team_task}, override=True, field="description", value="a" * 2049,
                 exc_type=ValueError, exc_str=f'Invalid description length, minimum 0 and maximum 2048 characters: "{"a" * 2049}"'),
    InitTestCase(data={**base_team_task}, override=True, field="contributors", value="user",
                 exc_type=ValueError, exc_str=f'Invalid contributors type: "{type("user")}"'),
    InitTestCase(data={**base_team_task}, override=True, field="contributors", value=[""],
                 exc_type=ValueError, exc_str="Contributor usernames cannot be empty"),
    InitTestCase(data={**base_team_task}, override=True, field="contributors", value=[123],
                 exc_type=ValueError, exc_str=f'Invalid contributor username type: "{type(123)}"'),
]


@pytest.fixture
def project():
    return Project(**base_project)


@pytest.mark.parametrize("test_case", valid_init_test_cases)
def test_valid_init(project, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    task = TeamTask(project=project, **test_case.data)
    for k, v in test_case.data.items():
        assert getattr(task, k) == v


@pytest.mark.parametrize("test_case", invalid_init_test_cases)
def test_invalid_init(project, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    with pytest.raises(test_case.exc_type) as exc_info:
        TeamTask(project=project, **test_case.data)

    assert test_case.exc_str in str(exc_info.value)

