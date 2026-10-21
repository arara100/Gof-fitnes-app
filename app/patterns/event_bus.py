"""Observer pattern: decouples "a workout was logged" from everything that reacts to it.

Why Observer here: finishing a workout must update statistics, achievements, challenges
and the leaderboard. `SessionService` only publishes `SessionCompleted` to the bus; each
reaction is an independent subscriber registered elsewhere, so features can be added or
removed without touching the service (Open/Closed, low coupling). A failing subscriber is
logged and never breaks logging of the workout itself.
"""
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SessionCompleted:
    user_id: int
    session_id: int
    workout_id: int
    duration_min: int
    calories: float
    performed_at: datetime


class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event_type, handler):
        if handler not in self._handlers[event_type]:  # idempotent: app factory may run many times
            self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(self, event):
        for handler in list(self._handlers[type(event)]):
            try:
                handler(event)
            except Exception:  # one broken observer must not affect the others
                logger.exception("Event handler %r failed for %r", handler, event)


# Shared application bus; subscribers are registered at app start-up.
event_bus = EventBus()
