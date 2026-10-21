from app.models import Achievement, Challenge, ChallengeParticipation, UserAchievement
from app.repositories.base import Repository


class AchievementRepository(Repository):
    model = Achievement

    def earned_ids(self, user_id):
        rows = UserAchievement.query.filter_by(user_id=user_id).all()
        return {r.achievement_id: r for r in rows}

    def by_code(self, code):
        return Achievement.query.filter_by(code=code).first()


class ChallengeRepository(Repository):
    model = Challenge

    def participation(self, user_id, challenge_id):
        return ChallengeParticipation.query.filter_by(
            user_id=user_id, challenge_id=challenge_id
        ).first()

    def participations_for_user(self, user_id):
        return ChallengeParticipation.query.filter_by(user_id=user_id).all()
