from datetime import date

from app.models import Challenge, ChallengeParticipation
from app.patterns.challenge_state import state_for
from app.repositories.social_repository import ChallengeRepository
from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError

EDITABLE = ("title", "description", "metric", "target", "start_date", "end_date")


class ChallengeService:
    """Challenges and participation. Phase rules come from ChallengeState."""

    def __init__(self, challenges=None, users=None):
        self.challenges = challenges or ChallengeRepository()
        self.users = users or UserRepository()

    def list(self):
        return self.challenges.list()

    def get(self, challenge_id):
        c = self.challenges.get(challenge_id)
        if not c:
            raise ServiceError("Challenge not found", 404)
        return c

    def status(self, challenge, on_date=None):
        return state_for(challenge, on_date or date.today()).name

    def join(self, user_id, challenge_id):
        challenge = self.get(challenge_id)
        # State: joining is allowed only in phases that say so.
        if not state_for(challenge, date.today()).can_join():
            raise ServiceError("Challenge is finished", 409)
        if self.challenges.participation(int(user_id), challenge_id):
            raise ServiceError("Already joined", 409)
        part = ChallengeParticipation(user=self.users.get(int(user_id)), challenge=challenge)
        self.challenges.add(part)
        self.challenges.commit()
        return part

    def my_participations(self, user_id):
        return {p.challenge_id: p for p in self.challenges.participations_for_user(int(user_id))}

    def add_progress(self, user_id, event):
        """Called by the observer: add the finished workout to every running challenge."""
        day = event.performed_at.date()
        for part in self.challenges.participations_for_user(user_id):
            challenge = part.challenge
            # State: only an active challenge accepts progress.
            if not state_for(challenge, day).accepts_progress():
                continue
            gain = {"sessions": 1, "calories": event.calories, "minutes": event.duration_min}[challenge.metric]
            part.progress = (part.progress or 0) + gain
        self.challenges.commit()

    def create(self, data):
        challenge = Challenge(**{k: data[k] for k in EDITABLE if k in data})
        self.challenges.add(challenge)
        self.challenges.commit()
        return challenge

    def update(self, challenge_id, data):
        c = self.get(challenge_id)
        for field in EDITABLE:
            if field in data:
                setattr(c, field, data[field])
        if c.end_date < c.start_date:
            raise ServiceError("end_date must not be before start_date", 422)
        self.challenges.commit()
        return c

    def delete(self, challenge_id):
        self.challenges.delete(self.get(challenge_id))
        self.challenges.commit()
