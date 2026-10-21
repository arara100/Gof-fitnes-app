from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.api.schemas import (
    WorkoutCreateSchema, WorkoutUpdateSchema, serialize_workout,
)
from app.api.utils import admin_required, load_json
from app.services.workout_service import WorkoutService

bp = Blueprint("workouts", __name__, url_prefix="/api")
service = WorkoutService()


@bp.get("/workouts")
@jwt_required()
def list_workouts():
    items = service.list(
        workout_type=request.args.get("type"),
        difficulty=request.args.get("difficulty"),
        query=request.args.get("q"),
    )
    return jsonify([serialize_workout(w) for w in items])


@bp.get("/workouts/<int:workout_id>")
@jwt_required()
def get_workout(workout_id):
    return jsonify(serialize_workout(service.get(workout_id)))


@bp.post("/admin/workouts")
@admin_required
def create_workout():
    workout = service.create(load_json(WorkoutCreateSchema()))
    return jsonify(serialize_workout(workout)), 201


@bp.put("/admin/workouts/<int:workout_id>")
@admin_required
def update_workout(workout_id):
    workout = service.update(workout_id, load_json(WorkoutUpdateSchema()))
    return jsonify(serialize_workout(workout))


@bp.delete("/admin/workouts/<int:workout_id>")
@admin_required
def delete_workout(workout_id):
    service.delete(workout_id)
    return "", 204
