from datetime import datetime

from app.models import Achievement, UserAchievement
from app.repositories.social_repository import AchievementRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError

EDITABLE = ("code", "title", "description", "metric", "threshold")


class AchievementService:
    def __init__(self, achievements=None, stats=None, users=None):
        self.achievements = achievements or AchievementRepository()
        self.stats = stats or StatsRepository()
        self.users = users or UserRepository()

    def list_for_user(self, user_id):
        earned = self.achievements.earned_ids(int(user_id))
        return [
            (a, earned[a.id].earned_at if a.id in earned else None)
            for a in self.achievements.list()
        ]

    def award_for(self, user_id):
        """Give every achievement whose threshold the user's totals now reach."""
        user = self.users.get(user_id)
        totals = self.stats.totals(user_id)
        earned = self.achievements.earned_ids(user_id)
        new = []
        for a in self.achievements.list():
            if a.id not in earned and totals.get(a.metric, 0) >= a.threshold:
                user.achievements.append(UserAchievement(achievement=a, earned_at=datetime.utcnow()))
                new.append(a)
        if new:
            self.achievements.commit()
        return new

    def create(self, data):
        if self.achievements.by_code(data["code"]):
            raise ServiceError("Achievement code already exists", 409)
        achievement = Achievement(**{k: data[k] for k in EDITABLE if k in data})
        self.achievements.add(achievement)
        self.achievements.commit()
        return achievement

    def update(self, achievement_id, data):
        a = self._get(achievement_id)
        for field in EDITABLE:
            if field in data:
                setattr(a, field, data[field])
        self.achievements.commit()
        return a

    def delete(self, achievement_id):
        self.achievements.delete(self._get(achievement_id))
        self.achievements.commit()

    def _get(self, achievement_id):
        a = self.achievements.get(achievement_id)
        if not a:
            raise ServiceError("Achievement not found", 404)
        return a
