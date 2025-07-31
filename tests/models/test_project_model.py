import pytest

from app import create_app
from app.models.project_model import Project
from app.utils import ProjectStateEnum

base_project = {
    "name": "project name",
    "state": ProjectStateEnum.ACTIVE,
    "start_date": "1970-01-01",
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
    InitTestCase(data={**base_project}, override=False),
    InitTestCase(data={**base_project}, override=True, field="start_date", value="1970-01-01"),
    InitTestCase(data={**base_project}, override=True, field="state", value=ProjectStateEnum.INACTIVE),
    InitTestCase(data={**base_project}, override=True, field="description", value="description"),
    InitTestCase(data={**base_project}, override=True, field="end_date", value="1970-01-01"),
    InitTestCase(data={**base_project}, override=True, field="description", value="description"),

    # boundary values
    InitTestCase(data={**base_project}, override=True, field="name", value="22"),
    InitTestCase(data={**base_project}, override=True, field="name", value="a" * 64),

    InitTestCase(data={**base_project}, override=True, field="description", value=""),  # 0
    InitTestCase(data={**base_project}, override=True, field="description", value="a" * 2048),
]

invalid_init_test_cases = [
    InitTestCase(data={**base_project}, override=True, field="name", value=None, exc_type=ValueError,
                 exc_str=f'Invalid name type: "{type(None)}"'),
    InitTestCase(data={**base_project}, override=True, field="name", value=123, exc_type=ValueError,
                 exc_str=f'Invalid name type: "{type(123)}"'),
    InitTestCase(data={**base_project}, override=True, field="name", value="a", exc_type=ValueError,
                 exc_str='Invalid name length, minimum 2 and maximum 64 characters: "a"'),

    InitTestCase(data={**base_project}, override=True, field="state", value=None, exc_type=ValueError,
                 exc_str=f'Invalid state type: "{type(None)}"'),
    InitTestCase(data={**base_project}, override=True, field="state", value=123, exc_type=ValueError,
                 exc_str=f'Invalid state type: "{type(123)}"'),
    InitTestCase(data={**base_project}, override=True, field="state", value="a", exc_type=ValueError,
                 exc_str=f'Invalid state type: "{type("a")}"'),

    InitTestCase(data={**base_project}, override=True, field="start_date", value=None, exc_type=ValueError,
                 exc_str=f'Invalid start_date type: "{type(None)}"'),
    InitTestCase(data={**base_project}, override=True, field="start_date", value=123, exc_type=ValueError,
                 exc_str=f'Invalid start_date type: "{type(123)}"'),
    InitTestCase(data={**base_project}, override=True, field="start_date", value="start_date", exc_type=ValueError,
                 exc_str='Invalid start_date format, expected "YYYY-MM-DD": "start_date"'),

    InitTestCase(data={**base_project}, override=True, field="end_date", value=123, exc_type=ValueError,
                 exc_str=f'Invalid end_date type: "{type(123)}"'),
    InitTestCase(data={**base_project}, override=True, field="end_date", value="end_date", exc_type=ValueError,
                 exc_str='Invalid end_date format, expected "YYYY-MM-DD": "end_date"'),

    InitTestCase(data={**base_project}, override=True, field="description", value=123, exc_type=ValueError,
                 exc_str=f'Invalid description type: "{type(123)}"'),
    InitTestCase(data={**base_project}, override=True, field="description", value="a" * 2049, exc_type=ValueError,
                 exc_str=f'Invalid description length, minimum 0 and maximum 2048 characters: "{"a" * 2049}"'),
]


# Because our model and ORM are coupled, and we do DB checks on the model, we need db context
@pytest.fixture
def app():
    flask = create_app()
    with flask.app_context() as ctx:
        yield


@pytest.mark.parametrize("test_case", valid_init_test_cases)
def test_valid_init(app, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    project = Project(**test_case.data)

    for k, v in test_case.data.items():
        assert getattr(project, k) == v


@pytest.mark.parametrize("test_case", invalid_init_test_cases)
def test_invalid_init(app, test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    with pytest.raises(test_case.exc_type) as exc_info:
        project = Project(**test_case.data)

    assert test_case.exc_str in str(exc_info.value)

