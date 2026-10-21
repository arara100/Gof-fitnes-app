"""Observers subscribed to `SessionCompleted` (see event_bus.py).

Each handler is one independent reaction to a logged workout: award achievements and add
progress to challenges. They are registered once at app start-up by `register_observers`.
"""
from app.patterns.event_bus import SessionCompleted, event_bus


def award_achievements(event):
    from app.services.achievement_service import AchievementService

    AchievementService().award_for(event.user_id)


def update_challenges(event):
    from app.services.challenge_service import ChallengeService

    ChallengeService().add_progress(event.user_id, event)


def register_observers(bus=event_bus):
    for handler in (award_achievements, update_challenges):
        bus.subscribe(SessionCompleted, handler)
