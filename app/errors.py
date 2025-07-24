import json

from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


def handle_http_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


def handle_validation_error(e: ValidationError):
    error = e.errors()[0]
    if "error" not in error["ctx"]:
        description = error["msg"]
    else:
        description = str(error["ctx"]["error"])  # extracting original exception

    return Response(
        response=json.dumps(
            {
                "error": HTTPStatus.UNPROCESSABLE_ENTITY,
                "name": "Unprocessable Entity",
                "description": description,
            }
        ),
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        content_type="application/json",
    )
