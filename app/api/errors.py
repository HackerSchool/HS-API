from http import HTTPStatus

from werkzeug.exceptions import HTTPException

from flask import jsonify,json, current_app as app
from flask import json

from app.extensions import db
from sqlalchemy import exc

class APIError(HTTPException):
    """ Exception to raise API Errors """
    def __init__(self, code: int, json):
        super().__init__(f"APIError: code: {code}, json: {json}")
        self.code = code
        self.json = json 

def throw_api_error(code, json: dict):
    raise APIError(code, json)

def handle_api_error(e: APIError):
    app.logger.warning(e)
    db.session.rollback()
    return jsonify(**{**e.json, "code": e.code}), e.code

def handle_http_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

def handle_invalid_input(e: ValueError):
    app.logger.warning(e)
    db.session.rollback()
    return jsonify({"error": str(e), "code": HTTPStatus.BAD_REQUEST}), HTTPStatus.BAD_REQUEST

def handle_db_integrity_exception(e: exc.IntegrityError):
    app.logger.warning(e)
    db.session.rollback()
    return jsonify({"error": str(e.orig), "code": HTTPStatus.CONFLICT}), HTTPStatus.CONFLICT

def handle_db_exceptions(e: exc.SQLAlchemyError):
    app.logger.warning(e)
    db.session.rollback()
    return jsonify({"error": "Internal server error", "code": HTTPStatus.INTERNAL_SERVER_ERROR}), HTTPStatus.INTERNAL_SERVER_ERROR
