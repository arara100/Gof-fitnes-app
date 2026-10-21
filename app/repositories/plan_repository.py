from app.models import WorkoutPlan
from app.repositories.base import Repository


class PlanRepository(Repository):
    model = WorkoutPlan

    def list_for_user(self, user_id):
        return WorkoutPlan.query.filter_by(user_id=user_id).order_by(WorkoutPlan.id).all()

    def get_for_user(self, plan_id, user_id):
        return WorkoutPlan.query.filter_by(id=plan_id, user_id=user_id).first()
