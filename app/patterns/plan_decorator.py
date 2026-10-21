"""Decorator pattern: optional extras (warm-up, stretching) layered over a plan view.

Why Decorator here: users may want any combination of warm-up and stretching around their
workouts, and those extras must not be stored in the database or change the plan itself.
Each decorator wraps a `PlanComponent`, adds its own entries to `entries()` and can be
stacked in any order, so combinations need no extra subclasses.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PlanEntry:
    day: int
    order: float
    title: str
    duration_min: int
    kind: str  # workout | warmup | stretch
    workout_id: int = None


class PlanComponent(ABC):
    @abstractmethod
    def entries(self):
        """Return plan entries sorted by (day, order)."""


class BasePlan(PlanComponent):
    """Plain plan as stored: one entry per PlanItem."""

    def __init__(self, plan):
        self._plan = plan

    def entries(self):
        return sorted(
            (PlanEntry(i.day_of_week, i.position, i.workout.title, i.workout.duration_min,
                       "workout", i.workout.id) for i in self._plan.items),
            key=lambda e: (e.day, e.order),
        )


class PlanDecorator(PlanComponent):
    def __init__(self, inner):
        self._inner = inner

    def entries(self):
        return self._inner.entries()


class WarmUpDecorator(PlanDecorator):
    """Adds a 5-minute warm-up before the first workout of every day."""

    def entries(self):
        base = self._inner.entries()
        firsts = {}
        for e in base:
            firsts.setdefault(e.day, e.order)
        extras = [PlanEntry(day, order - 1, "Розминка", 5, "warmup") for day, order in firsts.items()]
        return sorted(base + extras, key=lambda e: (e.day, e.order))


class StretchDecorator(PlanDecorator):
    """Adds 5 minutes of stretching after the last workout of every day."""

    def entries(self):
        base = self._inner.entries()
        lasts = {}
        for e in base:
            lasts[e.day] = e.order
        extras = [PlanEntry(day, order + 1, "Розтяжка", 5, "stretch") for day, order in lasts.items()]
        return sorted(base + extras, key=lambda e: (e.day, e.order))
