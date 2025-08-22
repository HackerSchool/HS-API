from werkzeug.local import LocalProxy
from flask import g, has_app_context

current_member = LocalProxy(lambda: _get_current_member())

def _get_current_member():
    """
    Retrieves the current member from Flask's application context global object `g`.
    This function is used by `LocalProxy` to provide easy access to the current member.
    """
    if has_app_context():
        return g.get("current_member", None)
    return None

