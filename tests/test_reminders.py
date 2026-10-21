from datetime import datetime, time

import pytest

from app.extensions import db
from app.models import Reminder
from app.patterns.notifier import Notifier
from app.services.reminder_service import ReminderService


def h(token):
    return {"Authorization": f"Bearer {token}"}


def test_reminder_crud(client, user_token):
    resp = client.post("/api/reminders", headers=h(user_token), json={"time": "07:30", "days": [0, 2, 4]})
    assert resp.status_code == 201
    rid = resp.get_json()["id"]
    assert resp.get_json()["time"] == "07:30" and resp.get_json()["days"] == [0, 2, 4]

    upd = client.put(f"/api/reminders/{rid}", headers=h(user_token), json={"enabled": False, "time": "08:00"})
    assert upd.get_json()["enabled"] is False and upd.get_json()["time"] == "08:00"
    assert len(client.get("/api/reminders", headers=h(user_token)).get_json()) == 1

    other = client.post("/api/auth/register", json={"email": "o@example.com", "password": "secret1"})
    other_token = other.get_json()["access_token"]
    assert client.put(f"/api/reminders/{rid}", headers=h(other_token), json={"enabled": True}).status_code == 404
    assert client.delete(f"/api/reminders/{rid}", headers=h(user_token)).status_code == 204


def test_reminder_validation(client, user_token):
    assert client.post("/api/reminders", headers=h(user_token), json={"time": "25:99"}).status_code == 422
    bad_day = client.post("/api/reminders", headers=h(user_token), json={"time": "07:00", "days": [9]})
    assert bad_day.status_code == 422


def _make(client, token, hhmm, days):
    client.post("/api/reminders", headers=h(token), json={"time": hhmm, "days": days})


def test_dispatch_due_once_per_day(client, user_token):
    _make(client, user_token, "07:30", [0])       # Monday
    _make(client, user_token, "07:31", [0])       # other minute
    _make(client, user_token, "07:30", [1])       # other weekday
    monday = datetime(2026, 10, 19, 7, 30)        # a Monday
    assert monday.weekday() == 0
    service = ReminderService()
    assert service.dispatch_due(monday) == 1
    assert service.dispatch_due(monday) == 0      # already sent today
    inbox = client.get("/api/notifications", headers=h(user_token)).get_json()
    assert len(inbox) == 1 and inbox[0]["is_read"] is False
    assert service.dispatch_due(datetime(2026, 10, 26, 7, 30)) == 1  # next Monday again


def test_disabled_reminder_not_sent(client, user_token):
    resp = client.post("/api/reminders", headers=h(user_token), json={"time": "07:30", "enabled": False})
    assert resp.status_code == 201
    assert ReminderService().dispatch_due(datetime(2026, 10, 19, 7, 30)) == 0


def test_mark_notification_read(client, user_token):
    _make(client, user_token, "07:30", [0])
    ReminderService().dispatch_due(datetime(2026, 10, 19, 7, 30))
    nid = client.get("/api/notifications", headers=h(user_token)).get_json()[0]["id"]
    assert client.post(f"/api/notifications/{nid}/read", headers=h(user_token)).get_json()["is_read"] is True
    assert client.get("/api/notifications?unread=1", headers=h(user_token)).get_json() == []
    assert client.post("/api/notifications/999/read", headers=h(user_token)).status_code == 404


def test_custom_notifier_channel(client, user_token):
    class Spy(Notifier):
        def __init__(self):
            self.sent = []

        def send(self, reminder, message):
            self.sent.append(reminder.id)

    _make(client, user_token, "07:30", [0])
    spy = Spy()
    ReminderService(notifiers=[spy]).dispatch_due(datetime(2026, 10, 19, 7, 30))
    assert len(spy.sent) == 1
