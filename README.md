# HS-API

## Intro
The HackerSchool API is an integrated database that accepts requests from the Internet via Flask framework. Its purpose is to ease the resource management process for the development teams and Human Resources. This system allows fetching member data, their projects, contributions, and other HackerSchool assets.
***
## Usage
The API will work on the hackerschool.dev/api endpoint, requiring member login to access the database. The endpoint is not yet set.

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
- GET    /members/{username}/tags          Get member tags
- PUT    /members/{username}/tags          Add member tags
- DELETE /members/{username}/tags          Delete member tags
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
