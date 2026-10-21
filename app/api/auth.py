from flask import Blueprint, jsonify

from app.api.schemas import LoginSchema, RegisterSchema, serialize_user
from app.api.utils import load_json
from app.services.auth_service import AuthService

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
service = AuthService()


@bp.post("/register")
def register():
    data = load_json(RegisterSchema())
    user = service.register(data["email"], data["password"], data.get("profile"))
    return jsonify(user=serialize_user(user), access_token=service.issue_token(user)), 201


@bp.post("/login")
def login():
    data = load_json(LoginSchema())
    return jsonify(access_token=service.login(data["email"], data["password"]))
