# HS-API

## Intro
The HackerSchool API is an integrated database that accepts requests from the Internet via Flask framework. Its purpose is to ease the resource management process for the development teams and Human Resources. This system allows fetching member data, their projects, contributions, and other HackerSchool assets.
***
## Usage
The API will work on the hackerschool.dev/api endpoint, requiring member login to access the database. The endpoint is not yet set.

### Members
> You will be able to execute the following member-related actions:
- **GET /members**: Retrieve a list of all members.
- **GET /members/{username}**: Retrieve details of a specific member by their ID.
- **POST /members**: Add a new member to the database.
- **PUT /members/{username}**: Update the details of an existing member by their ID.
- **DELETE /members/{username}**: Remove a member from the database by their ID.
- **GET /members/{username}/projects**: Get the projects a member is in.

### Projects
> You will be able to execute the following project-related actions:
- **GET /projects**: Retrieve a list of all projects.
- **POST /projects**: Create a new project.
- **GET /projects/{project_id}**: Retrieve details of a specific project by its ID.
- **PUT /projects/{project_id}**: Update an existing project by its ID.
- **DELETE /projects/{project_id}**: Delete a specific project by its ID.
- **GET /projects/{project_id}/members**: Retrieve a list of members for a specific project by its ID.

### Login
To access anything in the API, you need to login, there is a session limit for your activities - I have made an example code `APItester.py` for you to see.
***
## What now?
I will continue to work on this project and optimize it's feattures, if anyone wants to join I would much appreciate developing a *WebApp* to wrap the API command and give a GUI to the users.
### Soon...
I would very much like to add a command line application to wrap the API calls... HackerSchool should be managed bu a CLI...