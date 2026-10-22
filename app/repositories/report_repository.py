from sqlalchemy import func

from app.extensions import db
from app.models import User, Workout, WorkoutSession


class ReportRepository:
    def popular_workouts(self, date_from, date_to, limit):
        count = func.count(WorkoutSession.id)
        return (
            db.session.query(Workout.id, Workout.title, Workout.type, count,
                             func.sum(WorkoutSession.calories))
            .join(WorkoutSession, WorkoutSession.workout_id == Workout.id)
            .filter(WorkoutSession.performed_at >= date_from, WorkoutSession.performed_at <= date_to)
            .group_by(Workout.id, Workout.title, Workout.type)
            .order_by(count.desc(), Workout.id)
            .limit(limit)
            .all()
        )

    def activity_by_user(self, date_from, date_to):
        return (
            db.session.query(
                WorkoutSession.user_id, func.count(WorkoutSession.id),
                func.sum(WorkoutSession.duration_min), func.sum(WorkoutSession.calories),
            )
            .filter(WorkoutSession.performed_at >= date_from, WorkoutSession.performed_at <= date_to)
            .group_by(WorkoutSession.user_id)
            .all()
        )

    def count_users(self):
        return db.session.query(func.count(User.id)).scalar()
