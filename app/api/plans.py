from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import PlanCreateSchema, PlanGenerateSchema, serialize_plan
from app.api.utils import load_json
from app.services.plan_service import PlanService

bp = Blueprint("plans", __name__, url_prefix="/api/plans")
service = PlanService()


def _flag(name):
    return request.args.get(name, "").lower() in ("1", "true", "yes")


def _full(plan):
    entries = service.render(plan, warmup=_flag("warmup"), stretch=_flag("stretch"))
    return serialize_plan(plan, entries)


@bp.get("")
@jwt_required()
def list_plans():
    return jsonify([serialize_plan(p) for p in service.list(get_jwt_identity())])


@bp.post("")
@jwt_required()
def create_plan():
    data = load_json(PlanCreateSchema())
    plan = service.create_custom(get_jwt_identity(), data["name"], data["items"], data.get("goal"))
    return jsonify(_full(plan)), 201


@bp.post("/generate")
@jwt_required()
def generate_plan():
    data = load_json(PlanGenerateSchema())
    plan = service.generate(get_jwt_identity(), data.get("goal"), data.get("name"))
    return jsonify(_full(plan)), 201


@bp.get("/<int:plan_id>")
@jwt_required()
def get_plan(plan_id):
    return jsonify(_full(service.get(get_jwt_identity(), plan_id)))


@bp.delete("/<int:plan_id>")
@jwt_required()
def delete_plan(plan_id):
    service.delete(get_jwt_identity(), plan_id)
    return "", 204
