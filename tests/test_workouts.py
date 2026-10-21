from datetime import datetime

from app.extensions import db
from app.models import CardioWorkout, WorkoutSession, User
from app.patterns.workout_factory import CardioFactory, YogaFactory, get_factory
from app.services.errors import ServiceError

import pytest


def h(token):
    return {"Authorization": f"Bearer {token}"}


def test_factories_build_right_types_and_defaults():
    cardio = CardioFactory().create({"title": "Run", "duration_min": 30})
    yoga = YogaFactory().create({"title": "Flow", "duration_min": 20, "met": 2.5})
    assert cardio.type == "cardio" and cardio.met == 7.0 and cardio.difficulty == "medium"
    assert yoga.type == "yoga" and yoga.met == 2.5


def test_unknown_factory():
    with pytest.raises(ServiceError):
        get_factory("swimming")


def test_admin_crud_and_user_read(client, admin_token, user_token):
    created = client.post(
        "/api/admin/workouts", headers=h(admin_token),
        json={"type": "strength", "title": "Squats", "duration_min": 40, "difficulty": "hard"},
    )
    assert created.status_code == 201
    wid = created.get_json()["id"]
    assert created.get_json()["type"] == "strength"

    listing = client.get("/api/workouts?type=strength", headers=h(user_token)).get_json()
    assert [w["id"] for w in listing] == [wid]
    assert client.get("/api/workouts?type=yoga", headers=h(user_token)).get_json() == []
    assert client.get("/api/workouts?q=squa", headers=h(user_token)).get_json()[0]["id"] == wid

    upd = client.put(f"/api/admin/workouts/{wid}", headers=h(admin_token), json={"title": "Deep squats"})
    assert upd.get_json()["title"] == "Deep squats"

    assert client.delete(f"/api/admin/workouts/{wid}", headers=h(admin_token)).status_code == 204
    assert client.get(f"/api/workouts/{wid}", headers=h(user_token)).status_code == 404


def test_user_cannot_write(client, user_token):
    body = {"type": "yoga", "title": "X", "duration_min": 10}
    assert client.post("/api/admin/workouts", headers=h(user_token), json=body).status_code == 403
    assert client.post("/api/admin/workouts", json=body).status_code == 401


def test_validation(client, admin_token):
    resp = client.post("/api/admin/workouts", headers=h(admin_token),
                       json={"type": "swimming", "title": "X", "duration_min": 0})
    assert resp.status_code == 422


def test_cannot_delete_used_workout(client, admin_token):
    user = User(email="x@example.com", password_hash="x")
    workout = CardioWorkout(title="Run", duration_min=30)
    db.session.add(WorkoutSession(user=user, workout=workout, performed_at=datetime.utcnow(),
                                  duration_min=30, calories=100))
    db.session.commit()
    resp = client.delete(f"/api/admin/workouts/{workout.id}", headers=h(admin_token))
    assert resp.status_code == 409
