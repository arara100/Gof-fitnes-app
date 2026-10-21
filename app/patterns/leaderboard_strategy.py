"""Strategy pattern: which metric the leaderboard ranks users by.

Why Strategy here: the rating can be built from calories, number of workouts or active
minutes. Each strategy supplies the SQL aggregate for its metric, so `LeaderboardService`
and the query code stay identical and a new ranking is one small class added to
`_STRATEGIES`.
"""
from abc import ABC, abstractmethod

from sqlalchemy import func

from app.models import WorkoutSession
from app.services.errors import ServiceError


class LeaderboardStrategy(ABC):
    metric = None

    @abstractmethod
    def expression(self):
        """SQL aggregate computed per user over their sessions."""


class ByCalories(LeaderboardStrategy):
    metric = "calories"

    def expression(self):
        return func.sum(WorkoutSession.calories)


class BySessions(LeaderboardStrategy):
    metric = "sessions"

    def expression(self):
        return func.count(WorkoutSession.id)


class ByMinutes(LeaderboardStrategy):
    metric = "minutes"

    def expression(self):
        return func.sum(WorkoutSession.duration_min)


_STRATEGIES = {s.metric: s for s in (ByCalories(), BySessions(), ByMinutes())}

METRICS = tuple(_STRATEGIES)


def get_leaderboard_strategy(metric):
    try:
        return _STRATEGIES[metric]
    except KeyError:
        raise ServiceError(f"Unknown metric: {metric}", 422)
