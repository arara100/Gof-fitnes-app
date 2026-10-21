"""State pattern: what a challenge allows depends on where it is in its lifecycle.

Why State here: a challenge is Upcoming, Active or Finished purely by dates, and the rules
differ per phase (you can join before or during, progress counts only while active, a
finished one is frozen). Each phase is a class that answers `can_join` and
`accepts_progress`, so services and observers never compare dates themselves.
"""
from abc import ABC, abstractmethod


class ChallengeState(ABC):
    name = None

    @abstractmethod
    def can_join(self):
        """May a user join a challenge in this phase?"""

    @abstractmethod
    def accepts_progress(self):
        """Do completed workouts add to participants' progress in this phase?"""


class UpcomingState(ChallengeState):
    name = "upcoming"

    def can_join(self):
        return True

    def accepts_progress(self):
        return False


class ActiveState(ChallengeState):
    name = "active"

    def can_join(self):
        return True

    def accepts_progress(self):
        return True


class FinishedState(ChallengeState):
    name = "finished"

    def can_join(self):
        return False

    def accepts_progress(self):
        return False


_UPCOMING, _ACTIVE, _FINISHED = UpcomingState(), ActiveState(), FinishedState()


def state_for(challenge, on_date):
    if on_date < challenge.start_date:
        return _UPCOMING
    if on_date > challenge.end_date:
        return _FINISHED
    return _ACTIVE
