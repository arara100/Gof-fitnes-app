from sqlalchemy import func

from app.extensions import db
from app.models import User, WeightEntry, WorkoutSession


class StatsRepository:
    def totals(self, user_id, date_from=None, date_to=None):
        q = db.session.query(
            func.count(WorkoutSession.id),
            func.coalesce(func.sum(WorkoutSession.calories), 0),
            func.coalesce(func.sum(WorkoutSession.duration_min), 0),
            func.count(func.distinct(WorkoutSession.workout_id)),
        ).filter(WorkoutSession.user_id == user_id)
        if date_from:
            q = q.filter(WorkoutSession.performed_at >= date_from)
        if date_to:
            q = q.filter(WorkoutSession.performed_at <= date_to)
        sessions, calories, minutes, distinct = q.one()
        return {
            "sessions": sessions, "calories": float(calories),
            "minutes": int(minutes), "distinct_workouts": distinct,
        }

    def weight_entries(self, user_id, date_from=None, date_to=None):
        q = WeightEntry.query.filter_by(user_id=user_id)
        if date_from:
            q = q.filter(WeightEntry.date >= date_from.date())
        if date_to:
            q = q.filter(WeightEntry.date <= date_to.date())
        return q.order_by(WeightEntry.date).all()

    def get_weight_entry(self, user_id, day):
        return WeightEntry.query.filter_by(user_id=user_id, date=day).first()

    def daily_activity(self, user_id, date_from=None, date_to=None):
        day = func.date(WorkoutSession.performed_at)
        q = db.session.query(
            day, func.sum(WorkoutSession.calories), func.sum(WorkoutSession.duration_min)
        ).filter(WorkoutSession.user_id == user_id)
        if date_from:
            q = q.filter(WorkoutSession.performed_at >= date_from)
        if date_to:
            q = q.filter(WorkoutSession.performed_at <= date_to)
        return q.group_by(day).order_by(day).all()

    def leaderboard(self, expression, since=None, limit=20):
        value = expression.label("value")
        q = db.session.query(User.id, User.email, value).join(
            WorkoutSession, WorkoutSession.user_id == User.id
        )
        if since:
            q = q.filter(WorkoutSession.performed_at >= since)
        return q.group_by(User.id, User.email).order_by(value.desc()).limit(limit).all()
