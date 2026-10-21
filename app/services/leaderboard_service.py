from datetime import datetime, timedelta

from app.patterns.leaderboard_strategy import get_leaderboard_strategy
from app.repositories.stats_repository import StatsRepository

PERIODS = {"week": 7, "month": 30, "all": None}


class LeaderboardService:
    """Ranks users by a metric; the metric comes from a LeaderboardStrategy."""

    def __init__(self, stats=None):
        self.stats = stats or StatsRepository()

    def top(self, metric="calories", period="all", limit=20):
        # Strategy: the chosen metric decides which SQL aggregate is ranked.
        strategy = get_leaderboard_strategy(metric)
        days = PERIODS[period]
        since = datetime.utcnow() - timedelta(days=days) if days else None
        rows = self.stats.leaderboard(strategy.expression(), since, limit)
        return [
            {"rank": i, "user_id": uid, "name": email.split("@")[0], "value": round(float(v), 1)}
            for i, (uid, email, v) in enumerate(rows, start=1)
        ]
