from app.models import WorkoutSession
from app.repositories.base import Repository


class SessionRepository(Repository):
    model = WorkoutSession

    def list_for_user(self, user_id, date_from=None, date_to=None):
        q = WorkoutSession.query.filter_by(user_id=user_id)
        if date_from:
            q = q.filter(WorkoutSession.performed_at >= date_from)
        if date_to:
            q = q.filter(WorkoutSession.performed_at <= date_to)
        return q.order_by(WorkoutSession.performed_at.desc()).all()
