# HS-API

## Intro
The HackerSchool API is an integrated database that accepts requests from the Internet via Flask framework. Its purpose is to ease the resource management process for the development teams and Human Resources. This system allows fetching member data, their projects, contributions, and other HackerSchool assets.
***
## Usage
The API will work on the hackerschool.dev/api endpoint, requiring member login to access the database. The endpoint is not yet set.

## Running 

Before you can use the container you'll need to set up the sqlite database and create some directories. If you already have all directories related to data created and `.env` properly set up you can skip to step 2.

### Step 1
You'll need Flask to create the database and related storage directories that will be mounted onto the container.
Tweak and source the `.env` to point to where you want to store the application information in your host and to contain the admin user credentials (if you don't you won't have access to any endpoint, you can create a new user later and delete the admin one).
```
python -m .venv venv
source .venv/bin/activate
source .env
pip install -r requirements.txt
flask db-init
flask create-admin
```

### Step 2
If you are not going to develop you can get rid of Flask, you won't need it anymore! 
To get the container running simply run `docker compose up`.

## Development
For development user the Flask built in development server in a virtual environment. Don't forget to also source `.env` on development mode!
```sh
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run --debug
```

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
The authentication is session based. To login and get a session use the `/login` endpoint.

***
## What now?
I will continue to work on this project and optimize it's feattures, if anyone wants to join I would much appreciate developing a *WebApp* to wrap the API command and give a GUI to the users.

## CLI
A CLI for the API is available [here](https://github.com/HackerSchool/hs-cli).
