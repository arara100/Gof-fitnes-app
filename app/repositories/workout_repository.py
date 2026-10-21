from app.extensions import db
from app.models import PlanItem, Workout, WorkoutSession
from app.repositories.base import Repository


class WorkoutRepository(Repository):
    model = Workout

    def search(self, workout_type=None, difficulty=None, query=None):
        q = Workout.query
        if workout_type:
            q = q.filter(Workout.type == workout_type)
        if difficulty:
            q = q.filter(Workout.difficulty == difficulty)
        if query:
            q = q.filter(Workout.title.ilike(f"%{query}%"))
        return q.order_by(Workout.id).all()

    def is_in_use(self, workout_id):
        in_sessions = db.session.query(WorkoutSession.id).filter_by(workout_id=workout_id).first()
        in_plans = db.session.query(PlanItem.id).filter_by(workout_id=workout_id).first()
        return bool(in_sessions or in_plans)
