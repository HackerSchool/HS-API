from functools import wraps

from flask import session, jsonify

from app.api.extensions import tags_handler

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username')
        if not username:
            return jsonify({"message": "Unauthenticated access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

# def mandatory_tag(tag: str):
#     def decorator(f):
#         @wraps(f)
#         def wrapper(*args, **kwargs):
#             tags = session.get('tags').split(',')
#             if not tags_handler.can(tags, tag):
#                 return jsonify("message": tags_handler.ERROR_MESSAGE[tag]), 403
#             return f(*args, **kwargs)
#         return wrapper
#     return decorator