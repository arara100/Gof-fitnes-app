from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import ProfileSchema, serialize_user
from app.api.utils import load_json
from app.services.auth_service import AuthService

bp = Blueprint("users", __name__, url_prefix="/api/users")
service = AuthService()


@bp.get("/me")
@jwt_required()
def me():
    return jsonify(serialize_user(service.get_user(get_jwt_identity())))


@bp.put("/me")
@jwt_required()
def update_me():
    data = load_json(ProfileSchema())
    return jsonify(serialize_user(service.update_profile(get_jwt_identity(), data)))
