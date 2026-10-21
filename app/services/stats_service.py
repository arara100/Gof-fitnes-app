from datetime import date, datetime

from app.models import WeightEntry
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError


class StatsService:
    """Aggregated statistics and weight tracking for one user."""

    def __init__(self, stats=None, users=None):
        self.stats = stats or StatsRepository()
        self.users = users or UserRepository()

    def summary(self, user_id, date_from=None, date_to=None):
        user_id = int(user_id)
        totals = self.stats.totals(user_id, date_from, date_to)
        weights = self.stats.weight_entries(user_id, date_from, date_to)
        change = round(weights[-1].weight_kg - weights[0].weight_kg, 1) if len(weights) > 1 else 0.0
        return {**totals, "weight_change_kg": change}

    def progress(self, user_id, date_from=None, date_to=None):
        """Series for the progress chart: daily activity and weight over time."""
        user_id = int(user_id)
        return {
            "activity": [
                {"date": str(d), "calories": float(c or 0), "minutes": int(m or 0)}
                for d, c, m in self.stats.daily_activity(user_id, date_from, date_to)
            ],
            "weight": [
                {"date": w.date.isoformat(), "weight_kg": w.weight_kg}
                for w in self.stats.weight_entries(user_id, date_from, date_to)
            ],
        }

    def log_weight(self, user_id, weight_kg, day=None):
        user = self.users.get(int(user_id))
        if not user:
            raise ServiceError("User not found", 404)
        day = day or date.today()
        entry = self.stats.get_weight_entry(user.id, day)
        if entry:
            entry.weight_kg = weight_kg
        else:
            entry = WeightEntry(user=user, date=day, weight_kg=weight_kg)
            self.users.add(entry)
        latest = self.stats.weight_entries(user.id)
        if user.profile and (not latest or day >= max(e.date for e in latest)):
            user.profile.weight_kg = weight_kg
        self.users.commit()
        return entry

    def weights(self, user_id, date_from=None, date_to=None):
        return self.stats.weight_entries(int(user_id), date_from, date_to)
