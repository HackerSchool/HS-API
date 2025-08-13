import pytest
from app import create_app
from app.models.season_model import Season


app = create_app()
app.config.update({"TESTING": True})


base_season = {
    "season_number": 1,
    "start_date": "1970-01-01",
    "end_date": "1970-12-31",
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
    InitTestCase(data={**base_season}, override=False),
    InitTestCase(data={**base_season}, override=True, field="season_number", value=2),
    InitTestCase(data={**base_season}, override=True, field="start_date", value="1980-01-01"),
    InitTestCase(data={**base_season}, override=True, field="end_date", value="1980-12-31"),
    
    # boundary values
    InitTestCase(data={**base_season}, override=True, field="season_number", value=1),
    InitTestCase(data={**base_season}, override=True, field="start_date", value=None),
    InitTestCase(data={**base_season}, override=True, field="end_date", value=None),
]

invalid_init_test_cases = [
    # season_number
    InitTestCase(data={**base_season}, override=True, field="season_number", value="1",
                 exc_type=ValueError, exc_str='Invalid season_number type'),
    InitTestCase(data={**base_season}, override=True, field="season_number", value=0,
                 exc_type=ValueError, exc_str='expected integer greater than 0'),
    # start_date
    InitTestCase(data={**base_season}, override=True, field="start_date", value=123,
                 exc_type=ValueError, exc_str='Invalid start_date type'),
    InitTestCase(data={**base_season}, override=True, field="start_date", value="bad",
                 exc_type=ValueError, exc_str='Invalid start_date format'),
    # end_date
    InitTestCase(data={**base_season}, override=True, field="end_date", value=123,
                 exc_type=ValueError, exc_str='Invalid end_date type'),
    InitTestCase(data={**base_season}, override=True, field="end_date", value="bad",
                 exc_type=ValueError, exc_str='Invalid end_date format'),
]


@pytest.mark.parametrize("test_case", valid_init_test_cases)
def test_valid_init(test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    season = Season(**test_case.data)

    for k, v in test_case.data.items():
        assert getattr(season, k) == v


@pytest.mark.parametrize("test_case", invalid_init_test_cases)
def test_invalid_init(test_case: InitTestCase):
    if test_case.override:
        test_case.data[test_case.field] = test_case.value

    with pytest.raises(test_case.exc_type) as exc_info:
        season = Season(**test_case.data)

    assert test_case.exc_str in str(exc_info.value)
