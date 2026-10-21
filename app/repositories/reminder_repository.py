from app.models import Notification, Reminder
from app.repositories.base import Repository


class ReminderRepository(Repository):
    model = Reminder

    def list_for_user(self, user_id):
        return Reminder.query.filter_by(user_id=user_id).order_by(Reminder.time).all()

    def get_for_user(self, reminder_id, user_id):
        return Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()

    def enabled_at(self, hour, minute):
        return [r for r in Reminder.query.filter_by(enabled=True).all()
                if r.time.hour == hour and r.time.minute == minute]


class NotificationRepository(Repository):
    model = Notification

    def list_for_user(self, user_id, unread_only=False):
        q = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            q = q.filter_by(is_read=False)
        return q.order_by(Notification.created_at.desc(), Notification.id.desc()).all()

    def get_for_user(self, notification_id, user_id):
        return Notification.query.filter_by(id=notification_id, user_id=user_id).first()
