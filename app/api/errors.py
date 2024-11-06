from http import HTTPStatus

from werkzeug.exceptions import HTTPException

from flask import jsonify
from flask import json

from app.extensions import db
from sqlalchemy import exc

class APIError(Exception):
    """ Exception to raise API Errors """
    def __init__(self, code: int, json):
        super().__init__(f"APIError: code: {code}, json: {json}")
        self.code = code
        self.json = json 

def throw_api_error(code, json: dict):
    raise APIError(code, json)

def handle_api_error(e: APIError):
    print(e)
    return jsonify(**{**e.json, "code": e.code}), e.code

def handle_exception(e: HTTPException):
    """Return JSON instead of HTML for HTTP errors."""
    print(e)
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
    print(e)
    db.session.rollback()
    return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST

def handle_db_integrity_exception(e: exc.IntegrityError):
    print(e)
    db.session.rollback()
    return jsonify({"error": str(e.orig), "code": HTTPStatus.CONFLICT}), HTTPStatus.CONFLICT

def handle_db_exceptions(e: exc.SQLAlchemyError):
    # TODO log error
    print(e)
    db.session.rollback()
    return jsonify({"error": "Internal server error", "code": HTTPStatus.INTERNAL_SERVER_ERROR}), HTTPStatus.INTERNAL_SERVER_ERROR
