"""Strategy pattern: how calories burned in a session are calculated.

Why Strategy here: energy expenditure depends on the kind of workout (cardio intensity,
strength afterburn, yoga) and the formulas will be tuned or extended. `SessionService`
asks `get_calorie_strategy(workout.type)` and calls `calculate`; it contains no per-type
branching. A new workout type needs one new subclass registered in `_STRATEGIES`.

Base formula: kcal = MET * weight_kg * hours (standard compendium estimate).
"""
from abc import ABC, abstractmethod

DEFAULT_WEIGHT_KG = 70.0


class CalorieStrategy(ABC):
    @abstractmethod
    def modifier(self, workout):
        """Multiplier applied to the base estimate for this kind of workout."""

    def calculate(self, profile, workout, minutes):
        weight = (profile.weight_kg if profile and profile.weight_kg else DEFAULT_WEIGHT_KG)
        base = workout.met * weight * (minutes / 60.0)
        return round(base * self.modifier(workout), 1)


class CardioCalories(CalorieStrategy):
    """Cardio: harder sessions burn proportionally more than the base MET suggests."""

    _BY_DIFFICULTY = {"easy": 0.9, "medium": 1.0, "hard": 1.1}

    def modifier(self, workout):
        return self._BY_DIFFICULTY.get(workout.difficulty, 1.0)


class StrengthCalories(CalorieStrategy):
    """Strength: +10% for the afterburn effect (EPOC) that lasts after the session."""

    def modifier(self, workout):
        return 1.1


class YogaCalories(CalorieStrategy):
    """Yoga: the base estimate is already accurate for low-intensity work."""

    def modifier(self, workout):
        return 1.0


_STRATEGIES = {
    "cardio": CardioCalories(),
    "strength": StrengthCalories(),
    "yoga": YogaCalories(),
}


def get_calorie_strategy(workout_type):
    return _STRATEGIES.get(workout_type, YogaCalories())
