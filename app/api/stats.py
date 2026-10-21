from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import SessionQuerySchema, WeightSchema
from app.api.utils import load_json
from app.services.leaderboard_service import PERIODS, LeaderboardService
from app.patterns.leaderboard_strategy import METRICS
from app.services.errors import ServiceError
from app.services.stats_service import StatsService

bp = Blueprint("stats", __name__, url_prefix="/api")
stats = StatsService()
leaderboard = LeaderboardService()


def _range():
    q = SessionQuerySchema().load(request.args)
    return q.get("date_from"), q.get("date_to")


@bp.get("/stats")
@jwt_required()
def summary():
    return jsonify(stats.summary(get_jwt_identity(), *_range()))


@bp.get("/stats/progress")
@jwt_required()
def progress():
    return jsonify(stats.progress(get_jwt_identity(), *_range()))


@bp.post("/weight")
@jwt_required()
def log_weight():
    data = load_json(WeightSchema())
    entry = stats.log_weight(get_jwt_identity(), data["weight_kg"], data.get("date"))
    return jsonify(date=entry.date.isoformat(), weight_kg=entry.weight_kg), 201


@bp.get("/weight")
@jwt_required()
def list_weight():
    return jsonify([
        {"date": w.date.isoformat(), "weight_kg": w.weight_kg}
        for w in stats.weights(get_jwt_identity(), *_range())
    ])


@bp.get("/leaderboard")
@jwt_required()
def get_leaderboard():
    metric = request.args.get("metric", "calories")
    period = request.args.get("period", "all")
    if metric not in METRICS or period not in PERIODS:
        raise ServiceError(f"metric must be one of {METRICS}, period one of {tuple(PERIODS)}", 422)
    return jsonify(leaderboard.top(metric, period))
