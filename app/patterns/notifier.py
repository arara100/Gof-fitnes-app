"""Strategy pattern: the delivery channel of a reminder.

Why Strategy here: a reminder can be delivered in different ways (in-app notification now;
e-mail or push later). `ReminderService.dispatch_due` only calls `Notifier.send`, so adding
a channel means adding one subclass and passing it in `notifiers`, with no change to the
scheduling logic.
"""
from abc import ABC, abstractmethod

from app.extensions import db
from app.models import Notification


class Notifier(ABC):
    @abstractmethod
    def send(self, reminder, message):
        """Deliver `message` for `reminder` to its owner."""


class InAppNotifier(Notifier):
    """Stores a Notification row that the web UI shows in the user's inbox."""

    def send(self, reminder, message):
        db.session.add(Notification(user_id=reminder.user_id, reminder_id=reminder.id, message=message))
