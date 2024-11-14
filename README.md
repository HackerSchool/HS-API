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

## Technologies 
- Web App Framework - [Flask](https://github.com/pallets/flask)
- Session management - [Flask-Session](https://github.com/pallets-eco/flask-session/)
- ORM - [Flask-SQLAlchemy](https://github.com/pallets-eco/flask-sqlalchemy/)
- CORS - [Flask-Cors](https://github.com/corydolphin/flask-cors)
- Database - [sqlite3](https://docs.python.org/3/library/sqlite3.html)

## Setup 
### Prerequisites
Make sure you have the following installed:
- Python 3.x
- pip

### Installation
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
flask init-db
flask create-admin
```
6. **Run the application**:
```bash
flask run --debug
```


### Docker Setup (Optional)
1. **Create all application-data folders**: 
`docker compose` will mount the database and required folders into the container. For this you need to initialize the database, please refer to the [installation steps 1 to 5](#installation) to set this up.

1. **Build the docker image**:
```bash
docker compose build
```
2. **Run the application (with gunicorn)**:
```bash
docker compose up
```

## Environment Variables
**TLDR**: You can just `cp .env.example .env` to get all default environment variables ready.


- `SESSION_DIR`: Where to store session files (defaults to `data/flask_sessions/`)
- `SESSION_LIFETIME`: How long a session should last in seconds (defaults to 3 hours)

- `DATABASE_PATH`: Path to the `sqlite3` database file (defaults to `data/hackerschool.sqlite3`)
- `ROLES_PATH`:    Path to the roles configuration json file (defaults to `data/roles.json`)
- `PHOTOS_DIR`:    Path to the folder where user and project images will be stored (defaults to `data/photos/`)

- `LOG_LEVEL`:     Log level (defaults to INFO)
- `LOGS_PATH`      Path to logs file (deault to stdout)

These will only be necessary if you'll be using the `flask create-admin` command
- `ADMIN_USERNAME`:  Admin username
- `ADMIN_PASSWORD`:  Admin password


**Note**: If you use `docker compose` you will either need the `.env` file or environment variables set (no default values will be used) because `docker compose` will use use them to mount the correct volumes.

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
└── tests/             # components tests
    ├── models/
    │
    └── roles/
```
---
## Testing
To test run the following in the root directory of the repository:
```bash
python -m unittests -s discover
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

## Issues and To-Do
Known issues can be found [here](https://github.com/HackerSchool/HS-API/issues/5), and a to-do list [here](https://github.com/HackerSchool/HS-API/issues/7).

## Other 
- A [frontend](https://github.com/HackerSchool/HS-WebApp) application is currently under development.

- A CLI for the API is available [here](https://github.com/HackerSchool/hs-cli).

Contributions are welcomed!