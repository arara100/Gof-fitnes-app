from datetime import datetime

from app.patterns.calorie_strategy import get_calorie_strategy
from app.patterns.event_bus import SessionCompleted, event_bus
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workout_repository import WorkoutRepository
from app.models import WorkoutSession
from app.services.errors import ServiceError


class SessionService:
    """Logs completed workouts.

    Uses: CalorieStrategy (calories per workout type) and the Observer EventBus
    (publishes SessionCompleted after the session is saved).
    """

    def __init__(self, sessions=None, workouts=None, users=None, bus=None):
        self.sessions = sessions or SessionRepository()
        self.workouts = workouts or WorkoutRepository()
        self.users = users or UserRepository()
        self.bus = bus or event_bus

    def log(self, user_id, workout_id, duration_min=None, performed_at=None):
        user = self.users.get(int(user_id))
        workout = self.workouts.get(workout_id)
        if not user:
            raise ServiceError("User not found", 404)
        if not workout:
            raise ServiceError("Workout not found", 404)
        minutes = duration_min or workout.duration_min
        # Strategy: calorie formula is chosen by workout type.
        calories = get_calorie_strategy(workout.type).calculate(user.profile, workout, minutes)
        session = WorkoutSession(
            user=user, workout=workout, duration_min=minutes, calories=calories,
            performed_at=performed_at or datetime.utcnow(),
        )
        self.sessions.add(session)
        self.sessions.commit()
        # Observer: notify subscribers only after the data is safely stored.
        self.bus.publish(SessionCompleted(
            user_id=user.id, session_id=session.id, workout_id=workout.id,
            duration_min=minutes, calories=calories, performed_at=session.performed_at,
        ))
        return session

    def list(self, user_id, date_from=None, date_to=None):
        return self.sessions.list_for_user(int(user_id), date_from, date_to)
