from app.extensions import db
from functools import wraps

def transactional(fn):
    """ Decorate controllers whose DB operations should be performed in one transaction """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            r = fn(*args, **kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise
        return r
    return wrapper
