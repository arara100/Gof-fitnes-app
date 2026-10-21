from datetime import date, timedelta

import pytest

from app.extensions import db
from app.models import Achievement, CardioWorkout, Challenge
from app.patterns.challenge_state import ActiveState, FinishedState, UpcomingState, state_for
from app.patterns.leaderboard_strategy import get_leaderboard_strategy
from app.services.errors import ServiceError


def h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def run(app):
    w = CardioWorkout(title="Run", duration_min=30, met=7.0)
    db.session.add(w)
    db.session.commit()
    return w


def log(client, token, workout, when=None, minutes=None):
    body = {"workout_id": workout.id}
    if when:
        body["performed_at"] = when
    if minutes:
        body["duration_min"] = minutes
    return client.post("/api/sessions", headers=h(token), json=body)


def test_challenge_states():
    c = Challenge(start_date=date(2026, 5, 10), end_date=date(2026, 5, 20))
    assert isinstance(state_for(c, date(2026, 5, 9)), UpcomingState)
    assert isinstance(state_for(c, date(2026, 5, 10)), ActiveState)
    assert isinstance(state_for(c, date(2026, 5, 20)), ActiveState)
    assert isinstance(state_for(c, date(2026, 5, 21)), FinishedState)
    assert state_for(c, date(2026, 5, 9)).can_join() and not state_for(c, date(2026, 5, 9)).accepts_progress()
    assert not state_for(c, date(2026, 5, 21)).can_join()


def test_unknown_leaderboard_metric():
    with pytest.raises(ServiceError):
        get_leaderboard_strategy("steps")


def test_weight_and_stats(client, user_token, run):
    client.put("/api/users/me", headers=h(user_token), json={"weight_kg": 80})
    client.post("/api/weight", headers=h(user_token), json={"weight_kg": 80, "date": "2026-01-01"})
    client.post("/api/weight", headers=h(user_token), json={"weight_kg": 78.5, "date": "2026-02-01"})
    assert client.get("/api/users/me", headers=h(user_token)).get_json()["profile"]["weight_kg"] == 78.5
    log(client, user_token, run, "2026-01-05T08:00:00")
    log(client, user_token, run, "2026-01-06T08:00:00", minutes=60)
    s = client.get("/api/stats", headers=h(user_token)).get_json()
    assert s["sessions"] == 2 and s["minutes"] == 90 and s["distinct_workouts"] == 1
    assert s["weight_change_kg"] == -1.5
    prog = client.get("/api/stats/progress", headers=h(user_token)).get_json()
    assert len(prog["activity"]) == 2 and len(prog["weight"]) == 2


def test_achievement_awarded_by_observer(client, user_token, run):
    db.session.add(Achievement(code="first", title="First", metric="sessions", threshold=1))
    db.session.add(Achievement(code="ten", title="Ten", metric="sessions", threshold=10))
    db.session.commit()
    log(client, user_token, run)
    items = {a["code"]: a["earned"] for a in client.get("/api/achievements", headers=h(user_token)).get_json()}
    assert items == {"first": True, "ten": False}
    log(client, user_token, run)  # must not duplicate
    assert client.get("/api/achievements", headers=h(user_token)).status_code == 200


def test_challenge_progress_and_state_rules(client, user_token, admin_token, run):
    today = date.today()
    mk = lambda **kw: client.post("/api/admin/challenges", headers=h(admin_token), json={
        "title": "C", "metric": "minutes", "target": 100, **kw})
    active = mk(start_date=str(today - timedelta(days=1)), end_date=str(today + timedelta(days=5))).get_json()
    finished = mk(start_date="2020-01-01", end_date="2020-02-01").get_json()
    assert active["status"] == "active" and finished["status"] == "finished"

    assert client.post(f"/api/challenges/{finished['id']}/join", headers=h(user_token)).status_code == 409
    assert client.post(f"/api/challenges/{active['id']}/join", headers=h(user_token)).status_code == 201
    assert client.post(f"/api/challenges/{active['id']}/join", headers=h(user_token)).status_code == 409

    log(client, user_token, run)                                  # 30 min, today: counts
    log(client, user_token, run, "2020-01-10T08:00:00")           # outside the period: ignored
    got = client.get(f"/api/challenges/{active['id']}", headers=h(user_token)).get_json()
    assert got["progress"] == 30 and got["completed"] is False


def test_challenge_date_validation(client, admin_token):
    resp = client.post("/api/admin/challenges", headers=h(admin_token), json={
        "title": "Bad", "metric": "sessions", "target": 5,
        "start_date": "2026-05-10", "end_date": "2026-05-01"})
    assert resp.status_code == 422


def test_admin_achievement_crud_and_permissions(client, admin_token, user_token):
    body = {"code": "x", "title": "X", "metric": "calories", "threshold": 500}
    assert client.post("/api/admin/achievements", headers=h(user_token), json=body).status_code == 403
    created = client.post("/api/admin/achievements", headers=h(admin_token), json=body)
    assert created.status_code == 201
    assert client.post("/api/admin/achievements", headers=h(admin_token), json=body).status_code == 409
    aid = created.get_json()["id"]
    upd = client.put(f"/api/admin/achievements/{aid}", headers=h(admin_token), json={"threshold": 800})
    assert upd.get_json()["threshold"] == 800
    assert client.delete(f"/api/admin/achievements/{aid}", headers=h(admin_token)).status_code == 204


def test_leaderboard(client, user_token, run):
    other = client.post("/api/auth/register", json={"email": "bob@example.com", "password": "secret1"})
    bob = other.get_json()["access_token"]
    log(client, user_token, run, minutes=30)
    log(client, bob, run, minutes=60)
    rows = client.get("/api/leaderboard?metric=minutes", headers=h(user_token)).get_json()
    assert [(r["rank"], r["name"], r["value"]) for r in rows] == [(1, "bob", 60.0), (2, "u", 30.0)]
    by_sessions = client.get("/api/leaderboard?metric=sessions&period=week", headers=h(user_token)).get_json()
    assert {r["value"] for r in by_sessions} == {1.0}
    assert client.get("/api/leaderboard?metric=steps", headers=h(user_token)).status_code == 422
