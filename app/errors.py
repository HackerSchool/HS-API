# error handler functions to register in Flask
import json
from http import HTTPStatus

from flask import current_app, jsonify
from sqlalchemy import exc
from werkzeug.exceptions import HTTPException

from app.extensions import db

def handle_http_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    current_app.logger.info(e)
    db.session.rollback()
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


def handle_value_error(e: ValueError):
    current_app.logger.warning(e)
    db.session.rollback()
    return jsonify({"error": str(e), "code": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST


def handle_db_integrity_exception(e: exc.IntegrityError):
    current_app.logger.warning(e)
    db.session.rollback()
    return jsonify({"error": str(e.orig), "code": HTTPStatus.CONFLICT}), HTTPStatus.CONFLICT


def handle_db_exceptions(e: exc.SQLAlchemyError):
    current_app.logger.warning(e)
    db.session.rollback()
    return jsonify(
        {"error": "Internal server error", "code": HTTPStatus.INTERNAL_SERVER_ERROR}
    ), HTTPStatus.INTERNAL_SERVER_ERROR
