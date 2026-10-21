from functools import wraps

from flask import jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from marshmallow import ValidationError


def load_json(schema):
    """Validate the request body; ValidationError is turned into a 422 by the app handler."""
    return schema.load(request.get_json(silent=True) or {})


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt().get("role") != "admin":
            return jsonify(error="Admin access required"), 403
        return fn(*args, **kwargs)

    return wrapper


__all__ = ["admin_required", "load_json", "ValidationError"]
