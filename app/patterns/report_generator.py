"""Template Method pattern: the fixed skeleton shared by every report.

Why Template Method here: all reports follow the same steps (resolve period -> collect raw
rows -> aggregate them -> format the response envelope), and only the query and the
aggregation differ. `ReportGenerator.generate` is the template; subclasses override
`collect` and `aggregate` (and optionally `format`), so the envelope, period defaults and
ordering of steps live in one place and a new report is one small subclass.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta

DEFAULT_PERIOD_DAYS = 30


@dataclass(frozen=True)
class ReportParams:
    user_id: int = None
    date_from: datetime = None
    date_to: datetime = None
    limit: int = 10


class ReportGenerator(ABC):
    title = ""

    def __init__(self, stats=None, reports=None):
        from app.repositories.report_repository import ReportRepository
        from app.repositories.stats_repository import StatsRepository

        self.stats = stats or StatsRepository()
        self.reports = reports or ReportRepository()

    def generate(self, params):
        """The template method: fixed order of steps, not meant to be overridden."""
        params = self.resolve_period(params)
        raw = self.collect(params)
        data = self.aggregate(raw, params)
        return self.format(data, params)

    def resolve_period(self, params):
        date_to = params.date_to or datetime.utcnow()
        date_from = params.date_from or date_to - timedelta(days=DEFAULT_PERIOD_DAYS)
        return ReportParams(params.user_id, date_from, date_to, params.limit)

    @abstractmethod
    def collect(self, params):
        """Fetch raw rows from the repositories."""

    @abstractmethod
    def aggregate(self, raw, params):
        """Turn raw rows into the report's data payload."""

    def format(self, data, params):
        """Default envelope; override to change the output shape."""
        return {
            "report": self.title,
            "period": {"from": params.date_from.isoformat(), "to": params.date_to.isoformat()},
            "data": data,
        }


class ProgressReport(ReportGenerator):
    """A user's progress chart data: daily calories/minutes and weight over time."""

    title = "progress"

    def collect(self, params):
        return {
            "activity": self.stats.daily_activity(params.user_id, params.date_from, params.date_to),
            "weight": self.stats.weight_entries(params.user_id, params.date_from, params.date_to),
        }

    def aggregate(self, raw, params):
        activity = [{"date": str(d), "calories": float(c or 0), "minutes": int(m or 0)}
                    for d, c, m in raw["activity"]]
        weight = [{"date": w.date.isoformat(), "weight_kg": w.weight_kg} for w in raw["weight"]]
        return {
            "activity": activity,
            "weight": weight,
            "total_calories": round(sum(a["calories"] for a in activity), 1),
            "weight_change_kg": round(weight[-1]["weight_kg"] - weight[0]["weight_kg"], 1)
            if len(weight) > 1 else 0.0,
        }


class PopularWorkoutsReport(ReportGenerator):
    """Most frequently performed workouts across all users."""

    title = "popular_workouts"

    def collect(self, params):
        return self.reports.popular_workouts(params.date_from, params.date_to, params.limit)

    def aggregate(self, raw, params):
        return [
            {"rank": i, "workout_id": wid, "title": title, "type": wtype,
             "sessions": int(count), "total_calories": round(float(cal or 0), 1)}
            for i, (wid, title, wtype, count, cal) in enumerate(raw, start=1)
        ]


class AverageActivityReport(ReportGenerator):
    """Average activity of users in a period (per active user and per registered user)."""

    title = "average_activity"

    def collect(self, params):
        return {
            "rows": self.reports.activity_by_user(params.date_from, params.date_to),
            "total_users": self.reports.count_users(),
        }

    def aggregate(self, raw, params):
        rows, total_users = raw["rows"], raw["total_users"]
        active = len(rows)
        sessions = sum(r[1] for r in rows)
        minutes = sum(int(r[2] or 0) for r in rows)
        calories = sum(float(r[3] or 0) for r in rows)

        def avg(value, n):
            return round(value / n, 1) if n else 0.0

        return {
            "total_users": total_users,
            "active_users": active,
            "avg_per_active_user": {
                "sessions": avg(sessions, active), "minutes": avg(minutes, active),
                "calories": avg(calories, active),
            },
            "avg_per_registered_user": {
                "sessions": avg(sessions, total_users), "minutes": avg(minutes, total_users),
                "calories": avg(calories, total_users),
            },
        }
