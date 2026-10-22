from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity

from app.api.schemas import RoleSchema
from app.api.utils import admin_required, load_json
from app.services.user_admin_service import UserAdminService

bp = Blueprint("admin_users", __name__, url_prefix="/api/admin/users")
service = UserAdminService()


def _json(u):
    return {"id": u.id, "email": u.email, "role": u.role, "created_at": u.created_at.isoformat()}


@bp.get("")
@admin_required
def list_users():
    return jsonify([_json(u) for u in service.list()])


@bp.put("/<int:user_id>")
@admin_required
def set_role(user_id):
    data = load_json(RoleSchema())
    return jsonify(_json(service.set_role(get_jwt_identity(), user_id, data["role"])))


@bp.delete("/<int:user_id>")
@admin_required
def delete_user(user_id):
    service.delete(get_jwt_identity(), user_id)
    return "", 204
