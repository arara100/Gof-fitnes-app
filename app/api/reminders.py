from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import (
    ReminderSchema, ReminderUpdateSchema, serialize_notification, serialize_reminder,
)
from app.api.utils import load_json
from app.services.reminder_service import ReminderService

bp = Blueprint("reminders", __name__, url_prefix="/api")
service = ReminderService()


@bp.get("/reminders")
@jwt_required()
def list_reminders():
    return jsonify([serialize_reminder(r) for r in service.list(get_jwt_identity())])


@bp.post("/reminders")
@jwt_required()
def create_reminder():
    data = load_json(ReminderSchema())
    r = service.create(get_jwt_identity(), data["time"], data["days"], data["enabled"])
    return jsonify(serialize_reminder(r)), 201


@bp.put("/reminders/<int:reminder_id>")
@jwt_required()
def update_reminder(reminder_id):
    r = service.update(get_jwt_identity(), reminder_id, load_json(ReminderUpdateSchema()))
    return jsonify(serialize_reminder(r))


@bp.delete("/reminders/<int:reminder_id>")
@jwt_required()
def delete_reminder(reminder_id):
    service.delete(get_jwt_identity(), reminder_id)
    return "", 204


@bp.get("/notifications")
@jwt_required()
def list_notifications():
    unread = request.args.get("unread", "").lower() in ("1", "true", "yes")
    return jsonify([serialize_notification(n) for n in service.inbox(get_jwt_identity(), unread)])


@bp.post("/notifications/<int:notification_id>/read")
@jwt_required()
def read_notification(notification_id):
    return jsonify(serialize_notification(service.mark_read(get_jwt_identity(), notification_id)))
