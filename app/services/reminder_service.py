from datetime import datetime

from app.models import Reminder
from app.patterns.notifier import InAppNotifier
from app.repositories.reminder_repository import NotificationRepository, ReminderRepository
from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError

DEFAULT_MESSAGE = "Час для тренування! Не пропускайте сьогоднішнє заняття."


def _days_to_str(days):
    return ",".join(str(d) for d in sorted(set(days)))


def days_to_list(value):
    return [int(d) for d in value.split(",") if d != ""]


class ReminderService:
    """CRUD for reminders plus delivery of the ones that are due.

    Uses: Notifier (Strategy: delivery channel) when sending due reminders.
    """

    def __init__(self, reminders=None, notifications=None, users=None, notifiers=None):
        self.reminders = reminders or ReminderRepository()
        self.notifications = notifications or NotificationRepository()
        self.users = users or UserRepository()
        self.notifiers = notifiers or [InAppNotifier()]

    def list(self, user_id):
        return self.reminders.list_for_user(int(user_id))

    def _get(self, user_id, reminder_id):
        r = self.reminders.get_for_user(reminder_id, int(user_id))
        if not r:
            raise ServiceError("Reminder not found", 404)
        return r

    def create(self, user_id, time, days, enabled=True):
        user = self.users.get(int(user_id))
        if not user:
            raise ServiceError("User not found", 404)
        reminder = Reminder(user=user, time=time, days=_days_to_str(days), enabled=enabled)
        self.reminders.add(reminder)
        self.reminders.commit()
        return reminder

    def update(self, user_id, reminder_id, data):
        r = self._get(user_id, reminder_id)
        if "time" in data:
            r.time = data["time"]
        if "days" in data:
            r.days = _days_to_str(data["days"])
        if "enabled" in data:
            r.enabled = data["enabled"]
        self.reminders.commit()
        return r

    def delete(self, user_id, reminder_id):
        self.reminders.delete(self._get(user_id, reminder_id))
        self.reminders.commit()

    def dispatch_due(self, now=None, message=DEFAULT_MESSAGE):
        """Send every enabled reminder scheduled for this minute and weekday, once per day."""
        now = now or datetime.now()
        sent = 0
        for r in self.reminders.enabled_at(now.hour, now.minute):
            if now.weekday() not in days_to_list(r.days) or r.last_sent_date == now.date():
                continue
            # Strategy: every configured channel delivers the message.
            for notifier in self.notifiers:
                notifier.send(r, message)
            r.last_sent_date = now.date()
            sent += 1
        self.reminders.commit()
        return sent

    def inbox(self, user_id, unread_only=False):
        return self.notifications.list_for_user(int(user_id), unread_only)

    def mark_read(self, user_id, notification_id):
        n = self.notifications.get_for_user(notification_id, int(user_id))
        if not n:
            raise ServiceError("Notification not found", 404)
        n.is_read = True
        self.notifications.commit()
        return n
