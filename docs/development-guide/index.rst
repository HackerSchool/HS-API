Development Guide
======

If you are not directly developing the HS-API but rather using it please refer to usage section.

Overview
--------
This project follows a layered architecture, organized into the following core layers:

- **Controller** – Responsible for handling requests and orchestrating business logic.
- **Repository** – Manages data access, queries, and database transactions.
- **Models** – Defines the data structures and schema used throughout the application.

Each layer has its own dedicated directory in the project structure.

Core Libraries
--------------

This API is built using the following core Python libraries:

    - `Flask <https://flask.palletsprojects.com/en/stable/>`_ - Web Application Framework
    - `SQLAlchemy <https://docs.sqlalchemy.org/>`_ - ORM
    - `Pydantic <https://docs.pydantic.dev/latest/>`_ - Data validation and serialization
    - `Pytest <https://pytest.org/>`_ - Unit, component and integration testing

Setup
------
Use `uv` for easy setup

.. code-block:: sh

    pip install uv
    uv venv
    uv sync


Then you can start the development server py running ``uv run flask run``.
To create an admin user in the database you can use ``flask create-admin <name> <password>``.

The default ``.env.example`` contains the default configuration values, which are ideal for development.
Check out the :mod:`app.config.py` for more information.

Development
----------
In this section, we’ll demonstrate how to add the **Workshop** feature into the existing codebase, covering models, repositories, schemas, controllers and auth modules.

Models
~~~~~~~~
We begin by creating the **SQLAlchemy model**, which also serves as our domain entity.

.. code-block:: python

    # file app/models/workshop_model.py
    from sqlalchemy.orm import Mapped, mapped_column, validates

    from app.extensions import db
    from app.utils import is_valid_datestring

    class Workshop(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(unique=True)
        duration: Mapped[int] = mapped_column()

        def __init__(self, *, name=None, duration=None):
            self.name = name
            self.duration = duration

        @validates("name")
        def validate_name(self, k, v):
            if not isinstance(v, str):
               raise ValueError(f"Invalid name type: {type(v)}")
            return v

        @validates("duration")
        def validate_date(self, k, v):
            if not isinstance(v, int):
               raise ValueError(f"Invalid duration type: {type(v)}")
            if v <= 0:
               raise ValueError(f"Invalid dauration: {v}. Expected integer bigger than 0.)
            return v


We use ``mapped_column()`` to define attributes and SQL constraints, and the ``@validates`` decorator to enforce domain rules at the model level.

.. note::

    The domain logic is tightly coupled with SQLAlchemy here, which limits flexibility.

Repository
~~~~~~~~~~~
Next, we define a **repository** to handle data access and mutations for the Workshop entity.

.. code-block:: python

    # file app/repositories/workshop_repository.py
    from typing import List

    from app.models.workshop_model import Workshop
    from app.schemas.update_workshop_schema import UpdateWorkshopSchema

    class WorkshopRepository:
         def __init__(self, *, db: SQLAlchemy):
            self.db = db

         def create_workshop(self, workshop: Workshop) -> Workshop:
            self.db.session.add(gotten_workshop)
            returngotten_workshop

         def get_workshops(self) -> List[Workshops]:
             return self.db.session.execute(select(Workshop)).scalars().fetchall()

         def get_workshop_by_name(self, name: str) -> Workshop | None:
             return self.db.session.execute(select(Workshop).where(Workshop.name == name)).scalars().one_or_none()

         def update_workshop(self, workshop: Workshop, update_values: WorkshopUpdateSchema) -> Workshop:
             for k, v in update_values.model_dump(exclude_unset=True).items():
                 setattr(workshop, k, v)
             return workshop

         def delete_workshop(self, workshop: Workshop) -> str:
             self.db.session.execute(delete(Workshop).where(Workshop.name == workshop.name))
             return workshop.name

.. note::

    The repository can be injected into our controllers (which we’ll see next), making the application more modular, testable, and decoupled from the ORM.

Schemas
~~~~~~~~~~~

Before we implement the controller layer, we need to define the **schemas** that describe the structure of incoming and outgoing data. These schemas act as the interface between the client and the application, enforcing data shape and validation rules.

.. code-block:: python

    # file app/schemas/workshop_schema.py
    from pydantic import BaseModel, Field

    class WorkshopSchema(BaseModel):
        name: str = Field(...)
        duration: int = Field(..., gt=0)

.. code-block:: python

    # file app/schemas/update_workshop_schema.py
    from typing import Optional

    from pydantic import BaseModel, Field

    class UpdateWorkshopSchema(BaseModel):
        name: Optional[str] = Field(default=None)
        duration: Optional[int] = Field(default=None, gt=0)

We use **Pydantic** to define and validate the schema data. In this example, we defined two schemas for the Workshop entity.

.. note::

    Our current design uses Pydantic strictly for request validation, but it’s worth noting that Pydantic can also be used to define true domain models. This could help decouple the domain logic from the ORM entirely.

Controller
~~~~~~~~~~~
Now we can finally move into the **controller** layer. We will implement a Flask Blueprint factory.

.. code-block:: python

    # file app/controllers/workshop_controller.py
    from flask import Blueprint, request

    from app.models.workshop_model import Workshop
    from app.repository.workshop_repository import WorkshopRepository
    from app.schemas.workshop_schema import WorkshopSchema
    from app.schemas.update_workshop_schema import UpdateWorkshopSchema

    def create_workshop_blueprint(*, workshop_repository: WorkshopRepository)
        bp = Blueprint("workshops", __name__)

        @bp.route("/workshops", methods=["POST"])
        def create_workshop():
            workshop_data = WorkshopSchema(**request.json) # this enforces the validation, fails if invalid
            if workshop_repository.get_workshop_by_name(workshop_data.name) is not None:
                return abort(HTTPStatus.CONFLICT, description=f'Workshop with name "{workshop_data.name}" already exists.')

            workshop = workshop_repository.create_workshop(Workshop.from_schema(workshop_data))
            return WorkshopSchema.from_workshop(workshop).model_dump()


        @bp.route("/workshops/<name>", methods=["GET"])
        def get_workshop_by_name(name):
            if (workshop := workshop_repo.get_workshop_by_name(name=name)) is None:
                 return abort(HTTPStatus.NOT_FOUND, description=f'Workshop with name "{name}" not found')
             return WorkshopSchema.from_workshop(workshop).model_dump()

        @bp.route("/workshops/<name>", mehtods=["PUT"])
        def update_workshop(name):
             if (workshop := workshop_repository.get_workshop_by_name(name)) is None:
                 return abort(HTTPSTatus.NOT_FOUND, description=f'Workshop with name "{name}" not found.')

             workshop_update = UpdateWorkshopSchema(**request.json)
             if workshop_update.name and workshop_repository.get_workshop_by_name(workshop_update.name) is not None:
                 return abort(HTTPStatus.CONFLICT,
                            description=f'Workshop with name "{workshop_update.username}" already exists')

           updated_workshop = workshop_repository.update_workshop(workshop, workshop_update)
           return WorkshopSchema.from_workshop(updated_workshop).model_dump()

        return bp

As you can see there are a few methods being used by our schemas and models that were previously left out, let’s fill those in.

.. code-block:: python

    # file app/models/workshop_model.py
    from typing import TYPE_CHECKING
    from app.extensions import db

    if TYPE_CHECKING: # avoids circular imports
        from app.schemas.workshop_schema import WorkshopSchema

    class Workshop(db.Model):
        @classmethod
        def from_schema(self, schema: "WorkshopSchema"):
          return self(**schema.model_dump())

.. code-block:: python

    # file app/schemas/workshop_schema.py
    from pydantic import BaseModel

    class WorkshopSchema(BaseModel)
        @classmethod
        def from_workshop(self, workshop: Workshop)
          workshop_data = {}
          for field in cls.model_fields:
              if hasattr(workshop, field):
                  member_data[field] = getattr(workshop, field)
          return cls(**workshop_data)

Now to tie it all up we just need to register the blueprint in our application factory.

.. code-block:: python

    # file app/app.py
    from app.extensions import db
    from app.repositories.workshop_repository import WorkshopRepository
    from app.controllers.workshop_controller import create_workshop_bp

    def create_app(config_class=Config, *, workshop_repository=None):
        flask_app = Flask(__name__))
        flask_app.config.from_object(config_class)
        db.init_app(db)

        if workshop_repository is None:
            workshop_repository = WorkshopRepository(db=db)
        workshop_bp = create_workshop_bp(workshop_repository=workshop_repository)

        flask_app.register_blueprint(workshop_bp)

        return flask_app

Our endpoints should now be working, and expecting a JSON schema as declared in our schemas.

.. warning::

    ⚠️ Since we’re using SQLAlchemy models directly as domain entities our models validation is only enforced at the database layer. This means input validation via schemas is crucial to have better control of our domain objects.

.. note::

    A decorator :func:`app.decorators.transactional` is available to do each controller's operations in a single transaction and automatically commit or rollback on failure.

    .. code-block:: python

        @bp.route("/workshop/", methods=["POST"])
        @transactional
        def create_workshop():
            ...


Access
~~~~~~~

Now that we have working endpoints, we need to protect them. Our API requires **authentication**, as only HS members can use it, and it also includes a role-based **authorization** system.

The codebase provides a class, :class:`app.access.AccessController`, which offers some decorators we can use to protect our endpoints accordingly.

.. code-block:: python

    # file app/controllers/workshop_controller.py
    from app.access import AccessController

    def create_workshop_blueprint(*, workshop_repository: WorkshopRepository, access_controller: AccessController):
        bp = Blueprint("workshops", __name__)

        @bp.route("/workshops/<name>", methods=["POST"])
        @access_controller.requires_permission(general="workshop:update")
        def update_workshop(name):
            ...

The permission must also be defined in our permission configuration file for it to take effect.

.. code-block:: yaml

    scopes:
    - name: general
      roles:
      - name: sysadmin
        privilege: 100
        permissions:
          - workshop:update  # added here

This configuration grants users with the `sysadmin` role permission to access the *update_workshop* endpoint. The decorator also enforces login validation, so authentication is also taken care of.

If an endpoint only requires authentication you can also use the :func:`app.access.AccessController.requires_login` decorator.

.. code-block:: python

    @bp.route("/me", methods=["GET"])
    @access_controller.requires_login
    def me():
        ....

Testing
--------

In this section we will add tests for each layer of the Workshop entity. We use **Pytest** to write our tests and ensure the application is not broken!

Models
~~~~~~~

To test our models, we need to activate the Flask application context. We’ll define a pytest fixture to ensure the context is available when running our tests.

.. code-block:: python

    # file tests/models/test_workshop_model.py
    import pytest

    from app import create_app

    @pytest.fixture
    def app():
        flask = create_app()
        with flask.app_context() as ctx:
            yield

With the fixture in place, we can include the ``app`` fixture as a test parameter and safely instantiate models.

.. code-block:: python

    from app.models.workshop_model import Workshop

    def test_workshop_init(app):
        workshop = Workshop(name="name", duration=30)
        assert workshop.name = "name
        assert workshop.duration = 30

    def test_workshop_invalid_init(app):
        with pytest.raises(ValueError) as exc_info:
            workshop = Workshop(name="name", duration=-1)

        assert "Invalid duration" in str(exc_info)

Repositories
~~~~~~~~~~~~

Testing the repository layer requires a working database. For simplicity and isolation, we’ll use an **in-memory SQLite database**.

.. code-block:: python

    # file tests/repositories/test_workshop_repository.py
    import pytest

    from app import create_app
    from app.extensions import db
    from app.respoitories.workshop_repository import WorkshopRepository

    @pytest.fixture(scope="function")
    def app():
        Config.DATABASE_PATH = "sqlite:///:memory:"
        app = create_app()
        with app.app_context():
            db.create_all()
            yield
            db.session.commit() # flush transactions or it won't be able to drop
            db.drop_all()

    @pytest.fixture
    def workshop_repo():
        return WorkshopRepository(db=db)

We can now use the ``workshop_repo`` fixture in our tests to verify the repository methods behave correctly.

.. code-block:: python

    def test_get_workshop_by_name(app, workshop_repo: WorkshopRepository)
        workshop = Workshop(name="name", duration=30)
        db.session.add(workshop)
        gotten_workshop = member_repository.get_workshop_by_name(workshop.name)
        assert gotten_workshop is not None
        assert gotten_workshop.name == workshop.name
        assert gotten_workshop.duration == workshop.duration

    def test_create_workshop(app, workshop_repo: WorkshopRepository):
        workshop = Workshop(name="name", duration=30)
        workshop_repo.create_workshop(workshop)
        created_workshop = db.session.execute(select(Workshop).where(Workshop.name == workshop.name)).scalars().one_or_none()
        assert created_workshop is not None
        assert created_workshop.name == workshop.name
        assert created_workshop.duration == workshop.duration

Controllers
~~~~~~~~~~~~

To test the controllers, we’ll use Flask’s testing utilities alongside Python’s :mod:`unittest.mock` module to mock dependencies. This is where injecting repositories into our controllers gives us flexibility.

.. code-block:: python

    # file: tests/controllers/test_workshop_controller.py
    import pytest

    from unittest.mock import MagicMock
    from flask.testing import FlaskClient

    from app import create_app

    @pytest.fixture
    def mock_workshop_repo():
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(mock_workshop_repo):
        app = create_app(workshop_repo=mock_workshop_repo)
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

We now use our ``client`` fixture to request our controllers.

.. code-block:: python

    def test_get_workshop_name(client: FlaskClient, mock_workshop_repo: WorkshopRepoisotyr):
        mock_workshop_repo.get_workshop_by_name.return_value = Workshop(name="name", duration=30)
        rsp = client.get("/workshop/name")

        assert rsp.status_code == 200
        assert rsp.mimetype == "application/json"

        assert "name" in rsp.json and rsp.json["name"] == "name"
        assert "duration" in rsp.json and rsp.json["duration"] == 30

Schemas
~~~~~~~~
Testing schemas will be easier, as we only need to test our custom validators. For the Workshop entity example provided we didn't set any
custom validation, so let's add one.

.. code-block:: python

    # file app/schemas/workshop_schema.py
    from pydantic import BaseModel, Field, field_validator
    from app.utils import is_valid_datestring

    class WorkshopSchema(BaseModel):
        name: str = Field(...)
        duration: int = Field(..., gt=0)
        date: str = Field(...)

        @field_validator("date")
        @classmethod
        def validate_date(cls, v: str):
            if not is_valid_datestring(v)
                raise ValueError(
                    f'Invalid date format: "{v}". Expected format is "YYYY-MM-DD"'
                )
            return v

.. code-block:: python

    # file test/schemas/test_workshop_schema.py
    import pytest

    from app.schemas.workshop_schema import WorkshopSchema

    def test_datestring():
        workshop_data = WorkshopSchema(name="name", duration=30, date="1970-01-01")
        assert workshop_data.date = "1970-01-01"

    def test_invalid_datestring():
        with pytest.raises(ValueError) as exc_info:
            workshop_data = WorkshopSchema(name="name", duration=30, date="invalid date")

        assert exc_info.type == pydantic.ValidationError
        assert "Invalid date format" in str(exc_info.value.errors()[0].get("ctx", {}).get("error", None))


Extra
------
Now we have the workshop entity! However, there is something still missing. The workshop will have someone who is organizing it, so
we will need to connect it to a member! That will be left as a challenge to the developer who will be looking to follow this guide. :)
