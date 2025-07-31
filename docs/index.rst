.. HS-API documentation master file, created by
   sphinx-quickstart on Tue Jul 29 19:12:38 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

HS-API
====================

Welcome to the HS-API developer documentation. If you are not directly developing the HS-API but rather using it
please refer to the following documentation `HS-API usage <link URL>`_.

Overview
============
This project follows a **layered architecture**, organized into the following core layers:

- **Controller** – Responsible for handling requests and orchestrating business logic.
- **Repository** – Manages data access, queries, and database transactions.
- **Models** – Defines the data structures and schema used throughout the application.

Each layer has its own dedicated directory in the project structure.

Core Libraries
--------------

This API is built using the following core Python libraries:

- `Flask <https://flask.palletsprojects.com/en/stable/>`_ - The Web Application Framework
- `Flask-SQLAlchemy <https://flask-sqlalchemy.palletsprojects.com/>`_ – Used for ORM and database access.
- `Pydantic <https://docs.pydantic.dev/>`_ – Used for data validation and serialization.

Walkthrough
------------
In this section, we’ll demonstrate how to integrate a new entity — Workshop — into an existing codebase, covering models, repositories, schemas, and controllers.

We begin by creating the SQLAlchemy model, which also serves as our domain entity.
.. code-block:: python

   # file app/models/workshop_model.py
   from app.sqlalchemy.orm import Mapped, mapped_column, validates

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

We use mapped_column() to define attributes and SQL constraints, and the @validates decorator to enforce domain rules at the model level. Note that our domain logic is tightly coupled with SQLAlchemy here, which limits flexibility.
We start by declaring our models attributes using the ``mapped_column`` function and make use of
**SQLAlchemy** helpers such as ``validates`` to validate our data and enforce our domain constraints.

Unfortunately the domain and the ORM are highly coupled and, as a consequence, we end up relying a bit too much on **SQLAlchemy**
functionality.

Now we are ready to define our repository, which will expose various methods responsible for creating, fetching and updating our domain objects.

.. code-block:: python

   # file app/repositories/workshop_repository.py
   from typing import List

   from app.models.workshop_model import Workshop
   from app.schemas.update_workshop_schema import UpdateWorkshopSchema

   class WorkshopRepository:
        def __init__(self, *, db: SQLAlchemy):
           self.db = db

        def create_workshop(self, workshop: Workshop) -> Workshop:
           self.db.session.add(member)
           return member

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
Now we have a repository we can inject into our controllers (more on that later) which will make the application more modular and decoupled.

Before moving to the controllers we will take a look at the **schemas** module. If you notice our ``WorkshopRepository``
is made aware of a schema class on the ``update_workshop`` method.
Before we design the controllers it's good practice to define our application interface, that is, we must know what to expect from client requests
and what to send in return.

Our schemas describe this interface, for the Workshop entity we will define two possible schemas

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
We make use of **Pydantic** to validate our schemas (we should have used it to define a domain model too!).

Now we can finally move into the **controller** layer. We will implement a Flask Blueprint factory:

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
As you can see there are a few methods being used by our schemas and models that were previously left out, let's fill those in

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
Our endpoints should now be working, and expecting a JSON schema as declared in our **schemas**. It's **important** to note that,
because we do not have a real domain model and use SQLAlchemy models as our domain entities, we are not really enforcing
any constraints until the database is written to, so it's very crucial that the schemas validate the input correctly!

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`




