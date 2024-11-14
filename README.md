# HS-API

## Intro
The HackerSchool API is an integrated database that accepts requests from the Internet via the Flask framework. Its purpose is to ease the resource management process for development teams and Human Resources. This system allows the retrieval member data, their projects, contributions, and other HackerSchool assets.
***

## Running 
Before you can use the container, you'll need to set up the SQLite database and create some directories. If you already have all application-related directories created and `.env` properly set up, you can skip to Step 2.

### Step 1
You'll need Flask to create the database and related storage directories that will be mounted onto the container.
Adjust and source the `.env` to specify where you want to store application data on your host, and to include the admin user credentials (if you don't you won't have access to any endpoint, you can create a new user later and delete the admin one).
```sh
python -m venv .venv
source .venv/bin/activate
source .env
pip install -r requirements.txt
flask db-init
flask create-admin
```

### Step 2
If you are not planning to develop, you can get rid of Flask, you won't need it anymore! 
To start the container simply run `docker compose up`.

## Development
For development use the Flask built in development server in a virtual environment. Don't forget to also source `.env` and initiailze the db if necessary on development mode!
```sh
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run --debug
```

---
## Endpoints
### Auth
```txt
Endpoints:
- POST /login  Login
- GET  /logout Logout
```

### Members
```txt
Endpoints:
- GET    /members                          Get all members
- POST   /members                          Create member
- GET    /members/{username}               Get member
- PUT    /members/{username}               Update member
- DELETE /members/{username}               Delete member
- PUT    /members/{username}/edit_password Change password 
- POST   /members/{username}/{proj_name}   Add project to member
- DELETE /members/{username}/{proj_name}   Remove project from member
- GET    /members/{username}/projects      Get member projects
- GET    /members/{username}/logo          Get member logo
- PUT    /members/{username}/logo          Upload member logo
- DELETE /members/{username}/logo          Delete member logo
- GET    /members/{username}/roles         Get member roles 
- PUT    /members/{username}/roles         Add member roles 
- DELETE /members/{username}/roles         Delete member roles 
```

### Projects
```txt
Endpoints:
- GET    /projects                        Get all projects
- POST   /projects                        Create project
- GET    /projects/{proj_name}            Get project
- PUT    /projects/{proj_name}            Update project
- DELETE /projects/{proj_name}            Delete project
- POST   /projects/{proj_name}/{username} Add project to member
- DELETE /projects/{proj_name}/{username} Remove project from member
- GET    /projects/{proj_name}/members    Get project members
- GET    /projects/{proj_name}/logo       Get project logo
- PUT    /projects/{proj_name}/logo       Upload project logo
- DELETE /projects/{proj_name}/logo       Delete project logo
```
### Login
Authentication is session based. To login and start a session, use the `/login` endpoint.

---
## What now?
The next step is creating a frontend.

Known issues can be found [here](https://github.com/HackerSchool/HS-API/issues/5), and a TODO list [here](https://github.com/HackerSchool/HS-API/issues/7).

Contributions are welcomed!


## CLI
A CLI for the API is available [here](https://github.com/HackerSchool/hs-cli).
