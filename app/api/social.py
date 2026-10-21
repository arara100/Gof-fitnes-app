from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.api.schemas import (
    AchievementSchema, AchievementUpdateSchema, ChallengeSchema, ChallengeUpdateSchema,
    serialize_achievement, serialize_challenge,
)
from app.api.utils import admin_required, load_json
from app.services.achievement_service import AchievementService
from app.services.challenge_service import ChallengeService

bp = Blueprint("social", __name__, url_prefix="/api")
achievements = AchievementService()
challenges = ChallengeService()


def _challenge_json(c, mine):
    return serialize_challenge(c, challenges.status(c), mine.get(c.id))


@bp.get("/achievements")
@jwt_required()
def list_achievements():
    return jsonify([serialize_achievement(a, at) for a, at in achievements.list_for_user(get_jwt_identity())])


@bp.get("/challenges")
@jwt_required()
def list_challenges():
    mine = challenges.my_participations(get_jwt_identity())
    return jsonify([_challenge_json(c, mine) for c in challenges.list()])


@bp.get("/challenges/<int:challenge_id>")
@jwt_required()
def get_challenge(challenge_id):
    mine = challenges.my_participations(get_jwt_identity())
    return jsonify(_challenge_json(challenges.get(challenge_id), mine))


@bp.post("/challenges/<int:challenge_id>/join")
@jwt_required()
def join_challenge(challenge_id):
    challenges.join(get_jwt_identity(), challenge_id)
    mine = challenges.my_participations(get_jwt_identity())
    return jsonify(_challenge_json(challenges.get(challenge_id), mine)), 201


@bp.post("/admin/achievements")
@admin_required
def create_achievement():
    return jsonify(serialize_achievement(achievements.create(load_json(AchievementSchema())))), 201


@bp.put("/admin/achievements/<int:achievement_id>")
@admin_required
def update_achievement(achievement_id):
    a = achievements.update(achievement_id, load_json(AchievementUpdateSchema()))
    return jsonify(serialize_achievement(a))


@bp.delete("/admin/achievements/<int:achievement_id>")
@admin_required
def delete_achievement(achievement_id):
    achievements.delete(achievement_id)
    return "", 204


@bp.post("/admin/challenges")
@admin_required
def create_challenge():
    return jsonify(_challenge_json(challenges.create(load_json(ChallengeSchema())), {})), 201


@bp.put("/admin/challenges/<int:challenge_id>")
@admin_required
def update_challenge(challenge_id):
    c = challenges.update(challenge_id, load_json(ChallengeUpdateSchema()))
    return jsonify(_challenge_json(c, {}))


@bp.delete("/admin/challenges/<int:challenge_id>")
@admin_required
def delete_challenge(challenge_id):
    challenges.delete(challenge_id)
    return "", 204
