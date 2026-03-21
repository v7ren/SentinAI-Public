from functools import wraps
from flask import session, jsonify


def require_auth(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if session.get("user_id") is None:
            return jsonify({"error": "Unauthorized", "detail": "Please log in"}), 401
        return f(*args, **kwargs)
    return inner


def optional_auth(f):
    @wraps(f)
    def inner(*args, **kwargs):
        return f(*args, **kwargs)
    return inner
