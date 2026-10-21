"""Builder pattern: step-by-step construction of a `WorkoutPlan` aggregate.

Why Builder here: a plan is an aggregate (plan + ordered items) that can be assembled from
two different sources: a strategy-generated schedule or the user's own choices. The builder
gives both the same construction steps and validates the result once in `build()`, so
services never assemble `PlanItem` rows by hand.
"""
from app.models import PlanItem, WorkoutPlan
from app.services.errors import ServiceError


class PlanBuilder:
    def __init__(self):
        self._user = None
        self._name = None
        self._goal = None
        self._entries = []

    def for_user(self, user):
        self._user = user
        return self

    def named(self, name):
        self._name = name
        return self

    def goal(self, goal):
        self._goal = goal
        return self

    def add_workout(self, workout, day_of_week):
        if not 0 <= day_of_week <= 6:
            raise ServiceError("day_of_week must be between 0 and 6", 422)
        self._entries.append((day_of_week, workout))
        return self

    def build(self):
        if self._user is None:
            raise ServiceError("Plan needs an owner", 422)
        if not self._name:
            raise ServiceError("Plan needs a name", 422)
        if not self._entries:
            raise ServiceError("Plan must contain at least one workout", 422)
        plan = WorkoutPlan(user=self._user, name=self._name, goal=self._goal)
        for position, (day, workout) in enumerate(sorted(self._entries, key=lambda e: e[0])):
            plan.items.append(PlanItem(workout=workout, day_of_week=day, position=position))
        return plan
