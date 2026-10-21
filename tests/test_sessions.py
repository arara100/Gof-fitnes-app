import pytest

from app.extensions import db
from app.models import CardioWorkout, StrengthWorkout, YogaWorkout
from app.patterns.calorie_strategy import CardioCalories, StrengthCalories, YogaCalories, get_calorie_strategy
from app.patterns.event_bus import EventBus, SessionCompleted, event_bus
from app.models import Profile


def h(token):
    return {"Authorization": f"Bearer {token}"}


class Dummy:
    def __init__(self, met, difficulty="medium"):
        self.met, self.difficulty = met, difficulty


def test_calorie_strategies():
    profile = Profile(weight_kg=80)
    assert CardioCalories().calculate(profile, Dummy(7.0), 60) == 560.0
    assert CardioCalories().calculate(profile, Dummy(7.0, "hard"), 60) == 616.0
    assert StrengthCalories().calculate(profile, Dummy(5.0), 60) == 440.0
    assert YogaCalories().calculate(profile, Dummy(2.5), 30) == 100.0
    assert CardioCalories().calculate(None, Dummy(7.0), 60) == 490.0  # default 70 kg
    assert isinstance(get_calorie_strategy("strength"), StrengthCalories)


def test_event_bus_isolation():
    bus, received = EventBus(), []

    def broken(_):
        raise RuntimeError("boom")

    bus.subscribe(SessionCompleted, broken)
    bus.subscribe(SessionCompleted, received.append)
    event = SessionCompleted(1, 1, 1, 30, 100.0, None)
    bus.publish(event)
    assert received == [event]


def test_log_session_calculates_and_publishes(client, user_token):
    client.put("/api/users/me", headers=h(user_token), json={"weight_kg": 80})
    w = StrengthWorkout(title="Squats", duration_min=60, met=5.0)
    db.session.add(w)
    db.session.commit()

    events = []
    event_bus.subscribe(SessionCompleted, events.append)
    try:
        resp = client.post("/api/sessions", headers=h(user_token), json={"workout_id": w.id})
    finally:
        event_bus.unsubscribe(SessionCompleted, events.append)
    assert resp.status_code == 201
    assert resp.get_json()["calories"] == 440.0
    assert len(events) == 1 and events[0].calories == 440.0


def test_list_sessions_filter(client, user_token):
    w = YogaWorkout(title="Flow", duration_min=30, met=2.5)
    db.session.add(w)
    db.session.commit()
    client.post("/api/sessions", headers=h(user_token),
                json={"workout_id": w.id, "performed_at": "2026-01-10T08:00:00"})
    client.post("/api/sessions", headers=h(user_token),
                json={"workout_id": w.id, "duration_min": 20, "performed_at": "2026-02-10T08:00:00"})
    allr = client.get("/api/sessions", headers=h(user_token)).get_json()
    assert [s["duration_min"] for s in allr] == [20, 30]
    jan = client.get("/api/sessions?from=2026-01-01T00:00:00&to=2026-01-31T00:00:00", headers=h(user_token))
    assert len(jan.get_json()) == 1


def test_log_unknown_workout(client, user_token):
    assert client.post("/api/sessions", headers=h(user_token), json={"workout_id": 99}).status_code == 404
    assert client.get("/api/sessions").status_code == 401
