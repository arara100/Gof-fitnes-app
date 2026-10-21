from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import SessionCreateSchema, SessionQuerySchema, serialize_session
from app.services.session_service import SessionService
from app.api.utils import load_json

bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")
service = SessionService()


@bp.post("")
@jwt_required()
def log_session():
    data = load_json(SessionCreateSchema())
    session = service.log(
        get_jwt_identity(), data["workout_id"], data.get("duration_min"), data.get("performed_at")
    )
    return jsonify(serialize_session(session)), 201


@bp.get("")
@jwt_required()
def list_sessions():
    query = SessionQuerySchema().load(request.args)
    sessions = service.list(get_jwt_identity(), query.get("date_from"), query.get("date_to"))
    return jsonify([serialize_session(s) for s in sessions])
