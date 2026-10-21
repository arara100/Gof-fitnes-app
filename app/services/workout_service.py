from app.patterns.workout_factory import get_factory
from app.repositories.workout_repository import WorkoutRepository
from app.services.errors import ServiceError

EDITABLE = ("title", "description", "duration_min", "difficulty", "met")


class WorkoutService:
    def __init__(self, workouts=None):
        self.workouts = workouts or WorkoutRepository()

    def list(self, workout_type=None, difficulty=None, query=None):
        return self.workouts.search(workout_type, difficulty, query)

    def get(self, workout_id):
        workout = self.workouts.get(workout_id)
        if not workout:
            raise ServiceError("Workout not found", 404)
        return workout

    def create(self, data):
        workout = get_factory(data["type"]).create(data)
        self.workouts.add(workout)
        self.workouts.commit()
        return workout

    def update(self, workout_id, data):
        workout = self.get(workout_id)
        for field in EDITABLE:
            if field in data:
                setattr(workout, field, data[field])
        self.workouts.commit()
        return workout

    def delete(self, workout_id):
        workout = self.get(workout_id)
        if self.workouts.is_in_use(workout_id):
            raise ServiceError("Workout is used in plans or sessions", 409)
        self.workouts.delete(workout)
        self.workouts.commit()
