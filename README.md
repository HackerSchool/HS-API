# HS-API
![unittests](https://github.com/HackerSchool/HS-API/actions/workflows/unittests.yml/badge.svg)

The HackerSchool API is an integrated database that accepts requests from the Internet via the Flask framework. Its purpose is to ease the resource management process for development teams and Human Resources.

---

## Table of Contents

- [Features](#features)
- [Technologies](#extensions)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Endpoints](#endpoints)
- [Issues and To-do](#issues-and-to-do)
- [Other](#other)

## Features

- User authentication and role based authorization
- CRUD operations for members and projects
- Members and projects photos fetch and upload
- Authentication and registration using Fénix student account 

## Technologies & Extensions
- Web App Framework - [Flask](https://github.com/pallets/flask)
- Session management - [Flask-Session](https://github.com/pallets-eco/flask-session/)
- ORM - [Flask-SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy/)
- CORS - [Flask-Cors](https://github.com/corydolphin/flask-cors)
- Migrations - [Flask-Migrate](https://github.com/miguelgrinberg/flask-migrate)
- Database - [sqlite3](https://docs.python.org/3/library/sqlite3.html)

## Setup 
### Prerequisites
Make sure you have the following installed:
- Python 3.11
- pip

### Development 
1. **Clone the repository**:
```bash
git clone git@github.com:HackerSchool/HS-API.git
cd HS-API
```
2. **Create a virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate
```
3. **Install dependencies**:
```bash
pip install -r requirements.txt
```
4. **Setup environment variables**: Create a `.env` file and add any necessary environment variables (see [Environment Variables](#environment-variables) section).

5. **Setup the database and create an admin user**:
```bash
flask db upgrade 
flask create-admin
```
6. **Run the application**:
```bash
flask run --debug
```

7. **Extra**: For development purposes you can also run the command `flask populate-db` to add dummy data into the database.


## Environment Variables
**TLDR**: You can just `cp .env.example .env` to get all default environment variables ready.

- `SESSION_TYPE`: Backend for session data, redis or filesystem (defaults to filesystem)
- `SESSION_DIR`: Directory if filesystem session backend (defaults to `data/flask_sessions/`)
- `SESSION_REDIS`: Redis URI if redis session backend

- `SESSION_LIFETIME`: How long a session should last in seconds (defaults to 14 days)

- `DATABASE_PATH`: Path to the `sqlite3` database file (defaults to `data/db/hackerschool.sqlite3`)
- `STATIC_DIR`:    Path to the folder where user and project images will be stored (defaults to `data/static/`)
- `ROLES_PATH`:    Path to the roles configuration json file (defaults to `data/roles.json`)

- `LOGS_PATH`      Path to logs file (defaults to stdout)
- `FRONTEND_URI`   URI for the frontend (defaults to `http://localhost:3000` for dev)

These will only be necessary if you'll be using the `flask create-admin` command
- `ADMIN_USERNAME`:  Admin username
- `ADMIN_PASSWORD`:  Admin password

These variables are used if you want to allow authentication with Fénix
- `CLIENT_ID`
- `CLIENT_SECRET`
- `FENIX_REDIRECT_URI`: `<your-url>/fenix-auth-callback` is already implemented and either logs in or redirects to the frontend `register` endpoint.

## Project Structure
The project follows a layered architecture with a controller, service and models layer. 
```
+-------------+
|  Controller |
+-------------+
       ^
       |
       |
+-------------+
|   Service   |
+-------------+
     ^    ^
     |    |
     |    +---------------------+
     |                          |
+-------------+        +------------------+
|   Models    |        |  Other Handlers  | (e.g, logos handler in filesystem)
+-------------+        +------------------+
```
The structure is based on the Flask [factory extension pattern](https://flask.palletsprojects.com/en/stable/patterns/appfactories/#factories-extensions).
```txt
├── app/
│   ├── api/           # controller layer
│   │                  
│   ├── services/      # service layer
│   │                  
│   ├── models/        # database models layer
│   │                  
│   ├── commands/      # commands definitions (like init-db, create-admin)
│   │                  
│   ├── logos/         # logos extension
│   │                  
│   ├── roles/         # roles extension
│   │                  
│   ├── config.py      # flask configuration variables
│   │                  
│   ├── extensions.py  # loading extensions
│   │                  
│   └── __init__.py    # entrypoint with flask app factory
│
├── data/              # application files
│   └── roles.json     # roles configuration file
│
├── migrations/        # migration files (alembic)
│
└── tests/             # components tests
    ├── models/
    │
    └── roles/
```
---
## Testing
To test run the following in the root directory of the repository:
```bash
python -m unittest discover -s tests
```

## Endpoints
`Content-Type` refers to the response type for `GET` requests and request type for `POST`, `PUT` and `DELETE` requests.
`-` refers to unused. 

### Auth

| Method   | URL           | Content-Type | Description                     |
|----------|---------------|--------------|---------------------------------|
| `POST`   | `/login`      | `json`       | Login and set cookie session ID |
| `GET`    | `/logout`     | `json`       | Logout and end session          |

### Members

| Method   | URL                                     | Content-Type | Description                                               |
|----------|-----------------------------------------|--------------|-----------------------------------------------------------|
| `GET`    | `/members`                              |  `json`      | Get a list of all members                                 |
| `POST`   | `/members`                              |  `json`      | Create a new member                                       |
| `GET`    | `/members/{username}`                   |  `json`      | Get details of a specific member by username              |
| `PUT`    | `/members/{username}`                   |  `json`      | Update member details by username                         |
| `DELETE` | `/members/{username}`                   |  `-`         | Delete a member by username                               |
| `PUT`    | `/members/{username}/edit_password`     |  `json`      | Change member password by username                        |
| `POST`   | `/members/{username}/{proj_name}`       |  `json`      | Add a project to the member's list                        |
| `DELETE` | `/members/{username}/{proj_name}`       |  `-`         | Remove a project from the member's list of projects       |
| `GET`    | `/members/{username}/projects`          |  `json`      | Get a list of all projects a member is associated with    |
| `GET`    | `/members/{username}/logo`              |  `-`         | Get member's profile logo                                 |
| `PUT`    | `/members/{username}/logo`              |  `multipart/form-data`| Upload or update member's logo                   |
| `DELETE` | `/members/{username}/logo`              |  `-`         | Delete member's logo                                      |
| `GET`    | `/members/{username}/roles`             |  `json`      | Get roles assigned to a member                            |
| `PUT`    | `/members/{username}/roles`             |  `json`      | Add roles to the member                                   |
| `DELETE` | `/members/{username}/roles`             |  `json`      | Remove roles from the member 

### Projects

| Method | URL                                       | Content-Type |Description                                          |
|--------|-------------------------------------------|--------------|-----------------------------------------------------|
| `GET`    | `/projects`                             |`json`        | Get a list of all projects                          |
| `POST`   | `/projects`                             |`json`        | Create a new project                                |
| `GET`    | `/projects/{proj_name}`                 |`json`        | Get details of a specific project by project name   |
| `PUT`    | `/projects/{proj_name}`                 |`json`        | Update project details by project name              |
| `DELETE` | `/projects/{proj_name}`                 |`-`           | Delete a project by project name                    |
| `POST`   | `/projects/{proj_name}/{username}`      |`json`        | Add a member to the project                         |
| `DELETE` | `/projects/{proj_name}/{username}`      |`-`           | Remove a member from the project                    |
| `GET`    | `/projects/{proj_name}/members`         |`json`        | Get a list of all members associated with a project |
| `GET`    | `/projects/{proj_name}/logo`            |`image/*`     | Get project logo                                    |
| `PUT`    | `/projects/{proj_name}/logo`            |`multipart/form-data` | Upload or update project logo               |
| `DELETE` | `/projects/{proj_name}/logo`            |`-`           | Delete project logo                                 |

## Deployment

For deploying the application you can simply tweak your configuration on `docker-compose.yaml` and run `docker compose up`.
This runs the backend container alongside a session redis backend so these options should not be changed on the configuration. A docker volume is created to hold all relevant backend information, such as, static images, access logs, error logs and the database itself.

Useful commands to inspect the deployed containers:

Launch a sqlite3 shell on the backend database:
```sh
docker run --rm -it -v <hs-volume-name>:/data nouchka/sqlite3 /data/hackerschool.sqlite3
```

Launch a redis shell on the session backend:
```sh
docker run -it --network <hs-bridge-network> --rm redis redis-cli -h <hs-redis-container>
```

Open a shell with mounted volume to inspect logs:
```sh
docker run --rm -it -v <hs-volume-name>:/mnt apline sh
```
or you can directly open a shell inside the running container if it's up
```sh
docker exec -it <hs-backend-container> bash
```

## Issues and To-Do
Known issues can be found [here](https://github.com/HackerSchool/HS-API/issues/5), and a to-do list [here](https://github.com/HackerSchool/HS-API/issues/7).

## Other 
- A [frontend](https://github.com/HackerSchool/HS-WebApp) application is currently under development.

- A CLI for the API is available [here](https://github.com/HackerSchool/hs-cli).

Contributions are welcomed!