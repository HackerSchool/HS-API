import json

from pydantic import ValidationError

from http import HTTPStatus

from flask import Response
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
    if "ctx" in error:
        del error["ctx"]
    if "url" in error:
        del error["url"]
    return Response(
        response=json.dumps(
            {
                "code": HTTPStatus.UNPROCESSABLE_ENTITY,
                "name": "Unprocessable Entity",
                "description": "Validation error",
                "details": error
            }
        ),
        status=HTTPStatus.UNPROCESSABLE_ENTITY,
        content_type="application/json",
    )
