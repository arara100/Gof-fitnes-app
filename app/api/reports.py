from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import ReportQuerySchema
from app.api.utils import admin_required
from app.services.report_service import ReportService

bp = Blueprint("reports", __name__, url_prefix="/api/reports")
service = ReportService()


def _run(name, user_id=None):
    q = ReportQuerySchema().load(request.args)
    return jsonify(service.run(name, user_id, q.get("date_from"), q.get("date_to"), q["limit"]))


@bp.get("/progress")
@jwt_required()
def progress():
    return _run("progress", get_jwt_identity())


@bp.get("/popular")
@jwt_required()
def popular():
    return _run("popular")


@bp.get("/activity")
@admin_required
def activity():
    return _run("activity")
