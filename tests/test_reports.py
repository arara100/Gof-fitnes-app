from datetime import datetime, timedelta

import pytest

from app.extensions import db
from app.models import CardioWorkout, YogaWorkout
from app.patterns.report_generator import ReportGenerator, ReportParams


def h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def data(client, user_token):
    run = CardioWorkout(title="Run", duration_min=30, met=7.0)
    yoga = YogaWorkout(title="Flow", duration_min=60, met=2.5)
    db.session.add_all([run, yoga])
    db.session.commit()
    bob = client.post("/api/auth/register", json={"email": "bob@example.com", "password": "secret1"})
    bob_token = bob.get_json()["access_token"]
    now = datetime.utcnow()
    day = lambda n: (now - timedelta(days=n)).isoformat()

    def log(token, workout, when, minutes=None):
        body = {"workout_id": workout.id, "performed_at": when}
        if minutes:
            body["duration_min"] = minutes
        assert client.post("/api/sessions", headers=h(token), json=body).status_code == 201

    log(user_token, run, day(1))
    log(user_token, run, day(2))
    log(user_token, yoga, day(3))
    log(bob_token, run, day(1), minutes=60)
    log(bob_token, run, day(90))  # outside the default 30-day period
    client.post("/api/weight", headers=h(user_token), json={"weight_kg": 80, "date": str((now - timedelta(days=10)).date())})
    client.post("/api/weight", headers=h(user_token), json={"weight_kg": 78, "date": str(now.date())})
    return run, yoga


def test_template_method_order():
    calls = []

    class Spy(ReportGenerator):
        title = "spy"

        def __init__(self):
            pass

        def collect(self, params):
            calls.append("collect")
            return [1, 2]

        def aggregate(self, raw, params):
            calls.append("aggregate")
            return sum(raw)

        def format(self, data, params):
            calls.append("format")
            return super().format(data, params)

    result = Spy().generate(ReportParams())
    assert calls == ["collect", "aggregate", "format"]
    assert result["data"] == 3 and result["report"] == "spy"
    assert "from" in result["period"]


def test_progress_report(client, user_token, data):
    body = client.get("/api/reports/progress", headers=h(user_token)).get_json()
    assert body["report"] == "progress"
    assert len(body["data"]["activity"]) == 3
    assert body["data"]["weight_change_kg"] == -2.0
    assert body["data"]["total_calories"] > 0


def test_popular_report(client, user_token, data):
    body = client.get("/api/reports/popular?limit=5", headers=h(user_token)).get_json()
    rows = body["data"]
    assert [(r["title"], r["sessions"]) for r in rows] == [("Run", 3), ("Flow", 1)]
    assert rows[0]["rank"] == 1
    wide = client.get("/api/reports/popular?from=2000-01-01T00:00:00", headers=h(user_token)).get_json()
    assert wide["data"][0]["sessions"] == 4  # includes the old session


def test_activity_report_admin_only(client, user_token, admin_token, data):
    assert client.get("/api/reports/activity", headers=h(user_token)).status_code == 403
    body = client.get("/api/reports/activity", headers=h(admin_token)).get_json()["data"]
    assert body["total_users"] == 3 and body["active_users"] == 2
    assert body["avg_per_active_user"]["sessions"] == 2.0     # 4 sessions / 2 users
    assert body["avg_per_registered_user"]["sessions"] == 1.3  # 4 / 3


def test_report_validation_and_auth(client, user_token):
    assert client.get("/api/reports/progress").status_code == 401
    bad = client.get("/api/reports/popular?from=2026-02-01T00:00:00&to=2026-01-01T00:00:00", headers=h(user_token))
    assert bad.status_code == 422
    assert client.get("/api/reports/popular?limit=0", headers=h(user_token)).status_code == 422
