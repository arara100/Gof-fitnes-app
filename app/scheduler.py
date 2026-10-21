"""Background job that delivers due reminders every minute (APScheduler).

A single BackgroundScheduler is shared by the process (`_scheduler`); `start_scheduler`
is idempotent so repeated app-factory calls never start a second one.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
_scheduler = None


def start_scheduler(app):
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    def job():
        from app.services.reminder_service import ReminderService

        with app.app_context():
            try:
                sent = ReminderService().dispatch_due()
                if sent:
                    logger.info("Sent %d reminder(s)", sent)
            except Exception:
                logger.exception("Reminder job failed")

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(job, "cron", minute="*", id="reminders", max_instances=1, coalesce=True)
    _scheduler.start()
    return _scheduler
