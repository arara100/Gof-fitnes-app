"""Factory Method: each concrete factory knows how to build one kind of workout."""
from abc import ABC, abstractmethod

from app.models import CardioWorkout, StrengthWorkout, Workout, YogaWorkout
from app.services.errors import ServiceError


class WorkoutFactory(ABC):
    workout_class = Workout
    default_met = 5.0

    def create(self, data):
        return self.workout_class(
            title=data["title"],
            description=data.get("description"),
            duration_min=data["duration_min"],
            difficulty=data.get("difficulty", "medium"),
            met=data.get("met", self.default_met),
        )


class CardioFactory(WorkoutFactory):
    workout_class = CardioWorkout
    default_met = 7.0


class StrengthFactory(WorkoutFactory):
    workout_class = StrengthWorkout
    default_met = 5.0


class YogaFactory(WorkoutFactory):
    workout_class = YogaWorkout
    default_met = 3.0


_FACTORIES = {
    "cardio": CardioFactory(),
    "strength": StrengthFactory(),
    "yoga": YogaFactory(),
}

WORKOUT_TYPES = tuple(_FACTORIES)


def get_factory(workout_type):
    try:
        return _FACTORIES[workout_type]
    except KeyError:
        raise ServiceError(f"Unknown workout type: {workout_type}", 422)
