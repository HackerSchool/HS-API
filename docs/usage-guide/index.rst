Usage Guide
=================

Introduction
------------

This API offers CRUD operations over members, projects and participations in the context of HackerSchool.

**Notes**: In the requests examples we will be using `null` values for optional fields, but keep in mind that a null value will
attempt to set the entity value to null, if you wish to skip those optional fields don't include them in the JSON body.


Members
---------

``POST   /members``
~~~~~~~~~~~~~~~~~~~~
    **Description**
        Create a member

    **Request format**

        A member object, as follows

        .. code-block:: json

            {
              "username": "user123",             // required, string, 3-32 chars, alphanumeric only
              "name": "Alice Johnson",           // required, string, 1-512 chars
              "email": "alice@example.com",      // required, string, 1-512 chars

              "ist_id": "ist1123456",            // optional, string, pattern: ^ist1[0-9]{5,7}$
              "password": "secret123",           // optional, string, 6-256 chars
              "member_number": 42,               // optional, int > 0
              "course": "LEIC",                  // optional, string, 1-8 chars
              "roles": ["member", "rh"],         // optional, list of strings
              "join_date": "2023-01-15",         // optional, string, ISO 8601 date (YYYY-MM-DD)
              "exit_date": null,                 // optional, string, ISO 8601 date (YYYY-MM-DD)
              "description": "A long description here...", // optional, string, max 2048 chars
              "extra": null                      // optional, string, max 2048 chars
            }

    **Response format**
        The created member object without the `password` key

----

``GET    /members``
~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve a list of all registered members.

    **Request format**
        No request body required.

    **Response format**
        List of member objects without the `password` key.

----

``GET    /members/<username>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve member by username.

    **Request format**
        No request body required.

    **Response format**
        Member object without the `password` key.

----

``PUT    /members/<username>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Update an existing member’s information by their username.

    **Request format**

        Update member object, as follows

            .. code-block:: json

                {
                  "username": "user123",               /* optional, string, 3-32 chars, alphanumeric only */
                  "name": "Alice Johnson",             /* optional, string, 1-512 chars */
                  "email": "alice@example.com",        /* optional, string, 1-512 chars */
                  "password": "secret123",             /* optional, string, 6-256 chars */
                  "member_number": 42,                 /* optional, int > 0 */
                  "course": "LEIC",                    /* optional, string, 1-8 chars */
                  "roles": ["member", "rh"],           /* optional, list of strings */
                  "join_date": "2023-01-15",           /* optional, string, ISO 8601 date (YYYY-MM-DD) */
                  "exit_date": null,                   /* optional, string, ISO 8601 date (YYYY-MM-DD) */
                  "description": "A long description here...", /* optional, string,max 2048 chars */
                  "extra": null                       /* optional, string, max 2048 chars */
                }


    **Response format**
        Updated member object without the `password` key

----

``DELETE /members/<username>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Delete member by username.

    **Request format**
        No request body required.

    **Response format**

        .. code-block:: json

            {
                "description": "Member deleted successfully",
                "username": "username",
            }

----

``GET    /members/<username>/image``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve the profile image of a member by their username.

    **Request format**
        No request body required.

    **Response format**
        Binary image data with content type ``image/jpeg`` or ``image/png`` depending on the stored image format.

----

``POST   /members/<username>/image``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Update the profile image of a member by their username.

    **Request format**
        ``multipart/form-data`` containing the image file with a ``.png``, ``.jpg``, or ``.jpeg`` extension.

        The image is included in the multipart body as a part named ``file``, with the appropriate content type (``image/png`` or ``image/jpeg``).

    **Response format**

        .. code-block:: json

            {
                "description": "Member image uploaded successfully",
                "username": "username",
            }

----

``GET    /members/<username>/participations/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Get list of member's participations by username.

    **Request format**
        No request body required.

    **Response format**
        .. code-block:: json

            {
                "join_date": "2025-08-12",                // string, ISO 8601 date
                "project_name": "Platform Revamp",        // string, 2–255 chars
                "roles": ["coordinator", "participant"]   // array of strings
            }


Projects
--------

``POST   /projects``
~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Create a new project.

    **Request format**

        .. code-block:: json

            {
                "name": "HS API",               // required, string, 2–255 chars
                "state": "active",              // required, string, (enum: e.g., "active", "archived", "planned")
                "start_date": "2024-11-18",     // required, string, ISO 8601 date (YYYY-MM-D

                "end_date": null,               // optional, string, ISO 8601 date (YYYY-MM-DD)
                "description": "CRUD HS API",   // optional, string, max 2048 chars
            }


    **Response format**

        A project object, adds the `slug` key to the previous submitted object, as follows

        .. code-block:: json

            {
                "name": "HS API",                          // string, 2–255 chars
                "state": "active",                         // string (enum: e.g., "active", "archived", "planned")
                "start_date": "2025-08-12",                // string, required, ISO 8601 date (YYYY-MM-DD)
                "slug": "hs-api",                          // string, URL-safe identifier

                "end_date": null,                          // string or null, ISO 8601 date
                "description": "CRUD API for HackerSchool" // string or null, project description
            }

----

``GET    /projects``
~~~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve a list of all projects.

    **Request format**
        No request body required.

    **Response format**
        List of projects objects.
----

``GET    /projects/<slug>``
~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Get a project by slug.

    **Request format**
        No request body required.

    **Response format**
        Project object.
----

``PUT    /projects/<slug>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Update a project by slug.

    **Request format**
        Update project object, as follows

        .. code-block:: json

            {

                "name": "HackerSchool API",   // optional, string, 2–255 chars
                "state": null,                // optional, string (enum: e.g., "active", "archived", "planned")
                "start_date": null,           // optional, string, ISO 8601 date (YYYY-MM-DD)
                "end_date": null,             // optional, string, ISO 8601 date (YYYY-MM-DD)
                "description": null           // optional, string, project description
           }



    **Response format**
        The updated project object.

----

``DELETE /projects/<slug>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Delete a project by slug.

    **Request format**
        No request body required.

    **Response format**

        .. code-block:: json

            {
                "description": "Project deleted successfully",
                "name": "project name",
            }


----

``GET    /projects/<slug>/image``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve the profile image of a member by their username.

    **Request format**
        No request body required.

    **Response format**
        Binary image data with content type ``image/jpeg`` or ``image/png`` depending on the stored image format.

----

``POST   /projects/<slug>/image``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Update the image of a project by slug.

    **Request format**
        ``multipart/form-data`` containing the image file with a ``.png``, ``.jpg``, or ``.jpeg`` extension.

        The image is included in the multipart body as a part named ``file``, with the appropriate content type (``image/png`` or ``image/jpeg``).

    **Response format**

        .. code-block:: json

            {
                "description": "Project image uploaded successfully",
                "name": "project name",
            }

----

``POST   /projects/<slug>/participations``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Create a new participation entry for project by slug.

    **Request format**

        .. code-block:: json

            {
                "username": "johndoe",         // required, string, 3–32 chars, alphanumeric only
                "join_date": "2025-08-12",     // required, string, ISO 8601 date (YYYY-MM-DD)
                "roles": ["coordinator"]       // optional, array of strings
            }

    **Response format**
        A participation object, as follows

        .. code-block:: json

            {
                "username": "johndoe",         // string, required, 3–32 chars, alphanumeric only
                "join_date": "2025-08-12",     // string or null, optional, ISO 8601 date (YYYY-MM-DD)
                "project_name": "HS API",      // string or null, optional, 2–255 chars
                "roles": ["coordinator"]       // array of strings or null, optional
            }


----

``GET    /projects/<slug>/participations``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve a list of all participations in a specific project by slug.

    **Request format**
        No request body required.

    **Response format**
        A participation object without the `project_name` field.

----


``GET    /projects/<slug>/participations/<username>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    **Description**
        Retrieve details about a specific member’s participation in a project, identified by project slug and member username.

    **Request format**
        No request body required.

    **Response format**
        A participation object.


----

Authentication
----------------

Authentication is session based using cookies. The client authenticates with the API, at which point a session is created
server side and a cookie is sent back with the session ID to identify the client in future requests.

You can initiate a session with a traditional login password or through Fenix.

``POST /login```
~~~~~~~~~~~~~~~~~~~
    **Description**
        Login with username and password

    **Request format**
        .. code-block:: json

            {
                "username": "username",
                "password": "password",
            }

    **Response format**
        .. code-block:: json

            {
                "member": {} // logged in member object
                "description": "Logged in successfully!"
            }

----

``GET  /fenix-login```
~~~~~~~~~~~~~~~~~~~
The Fenix authentication is made using OAuth 2.0 and the ``/fenix-login`` endpoint starts the OAuth Flow.

Once the flow is complete and if the user's IST ID is also present in the database, then the authentication is complete and the
the same response as ``POST /login`` is sent.

----

Errors
-------
All application errors are returned as follows:

    .. code-block:: json

        {
            "code": "404",
            "name": "Not Found",
            "description": "Member with username 'username' not found",
            "details": {} // optional, set by 422 errors to inform the invalid fields of the request
        }


Custom application errors:
    - **401 Unauthorized**: User doesn't have a session or invalid credentials provided.

    - **403 Forbidden**: User has no permission to perform the action.

    - **404 Not Found**: Request entities that do not exist.

    - **413 Request Entity Too Large**: Upload of the image is too big.

    - **422 Unprocessable Content**: Invalid JSON schema in request.

