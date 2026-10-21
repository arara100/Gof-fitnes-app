"""Strategy pattern: how a personal workout program is composed for a given goal.

Why Strategy here: the weekly schedule rules differ per goal (lose weight, gain muscle,
endurance) and new goals will appear. `PlanService.generate` only talks to the abstract
`PlanStrategy`, so adding a goal means adding one subclass and registering it in
`_STRATEGIES`, with no `if goal == ...` branches in the service (Open/Closed principle).
"""
from abc import ABC, abstractmethod

from app.services.errors import ServiceError

MON, TUE, WED, THU, FRI, SAT = range(6)


class PlanStrategy(ABC):
    """Chooses which workouts go on which days of the week."""

    goal = None

    @abstractmethod
    def schedule(self):
        """Return a list of (day_of_week, workout_type) pairs describing the week."""

    def select(self, workouts_by_type):
        """Fill the schedule with concrete workouts, rotating through those available.

        `workouts_by_type` maps a type ('cardio', ...) to a list of Workout objects.
        Types with no workouts in the library are skipped.
        """
        counters = {}
        selected = []
        for day, workout_type in self.schedule():
            pool = workouts_by_type.get(workout_type) or []
            if not pool:
                continue
            index = counters.get(workout_type, 0)
            selected.append((day, pool[index % len(pool)]))
            counters[workout_type] = index + 1
        return selected


class LoseWeightStrategy(PlanStrategy):
    """Cardio-heavy week with strength and yoga for recovery, to maximise calorie burn."""

    goal = "lose_weight"

    def schedule(self):
        return [(MON, "cardio"), (TUE, "strength"), (WED, "cardio"),
                (THU, "yoga"), (FRI, "cardio"), (SAT, "strength")]


class GainMuscleStrategy(PlanStrategy):
    """Four strength days, one light cardio day and a yoga day for mobility."""

    goal = "gain_muscle"

    def schedule(self):
        return [(MON, "strength"), (TUE, "strength"), (WED, "cardio"),
                (THU, "strength"), (FRI, "strength"), (SAT, "yoga")]


class EnduranceStrategy(PlanStrategy):
    """Mostly cardio with one strength day and one yoga day."""

    goal = "endurance"

    def schedule(self):
        return [(MON, "cardio"), (TUE, "cardio"), (WED, "yoga"),
                (THU, "cardio"), (FRI, "strength"), (SAT, "cardio")]


_STRATEGIES = {s.goal: s for s in (LoseWeightStrategy(), GainMuscleStrategy(), EnduranceStrategy())}

GOALS = tuple(_STRATEGIES)


def get_strategy(goal):
    try:
        return _STRATEGIES[goal]
    except KeyError:
        raise ServiceError(f"Unknown goal: {goal}", 422)
