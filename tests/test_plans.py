import pytest

from app.extensions import db
from app.models import CardioWorkout, StrengthWorkout, YogaWorkout
from app.patterns.plan_builder import PlanBuilder
from app.patterns.plan_decorator import BasePlan, StretchDecorator, WarmUpDecorator
from app.patterns.plan_strategy import EnduranceStrategy, LoseWeightStrategy, get_strategy
from app.services.errors import ServiceError


def h(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def library(app):
    items = [
        CardioWorkout(title="Run", duration_min=30), CardioWorkout(title="HIIT", duration_min=20),
        StrengthWorkout(title="Squats", duration_min=40), YogaWorkout(title="Flow", duration_min=25),
    ]
    db.session.add_all(items)
    db.session.commit()
    return items


def test_strategy_schedules_differ_and_rotate(library):
    by_type = {}
    for w in library:
        by_type.setdefault(w.type, []).append(w)
    lose = LoseWeightStrategy().select(by_type)
    endurance = EnduranceStrategy().select(by_type)
    assert [d for d, _ in lose] == [0, 1, 2, 3, 4, 5]
    assert [w.title for d, w in lose if w.type == "cardio"] == ["Run", "HIIT", "Run"]
    assert sum(w.type == "cardio" for _, w in endurance) == 4


def test_strategy_skips_missing_types():
    assert LoseWeightStrategy().select({"cardio": []}) == []


def test_unknown_goal():
    with pytest.raises(ServiceError):
        get_strategy("fly")


def test_builder_validation():
    with pytest.raises(ServiceError):
        PlanBuilder().named("x").build()
    with pytest.raises(ServiceError):
        PlanBuilder().add_workout(object(), 9)


def test_decorators_stack(app, library):
    from app.models import User

    user = User(email="a@b.c", password_hash="x")
    plan = PlanBuilder().for_user(user).named("P").add_workout(library[0], 0).add_workout(library[2], 0).build()
    base = BasePlan(plan).entries()
    assert [e.kind for e in base] == ["workout", "workout"]
    both = StretchDecorator(WarmUpDecorator(BasePlan(plan))).entries()
    assert [e.kind for e in both] == ["warmup", "workout", "workout", "stretch"]


def test_generate_from_profile_goal(client, user_token, library):
    client.put("/api/users/me", headers=h(user_token), json={"goal": "gain_muscle"})
    resp = client.post("/api/plans/generate", headers=h(user_token), json={})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["goal"] == "gain_muscle" and len(body["entries"]) == 6


def test_generate_requires_goal(client, user_token, library):
    assert client.post("/api/plans/generate", headers=h(user_token), json={}).status_code == 422


def test_custom_plan_with_decorators_and_ownership(client, user_token, library):
    resp = client.post("/api/plans", headers=h(user_token), json={
        "name": "Mine", "items": [{"workout_id": library[0].id, "day_of_week": 1}],
    })
    assert resp.status_code == 201
    pid = resp.get_json()["id"]
    full = client.get(f"/api/plans/{pid}?warmup=1&stretch=true", headers=h(user_token)).get_json()
    assert [e["kind"] for e in full["entries"]] == ["warmup", "workout", "stretch"]

    other = client.post("/api/auth/register", json={"email": "o@example.com", "password": "secret1"})
    other_token = other.get_json()["access_token"]
    assert client.get(f"/api/plans/{pid}", headers=h(other_token)).status_code == 404
    assert client.delete(f"/api/plans/{pid}", headers=h(other_token)).status_code == 404
    assert client.delete(f"/api/plans/{pid}", headers=h(user_token)).status_code == 204


def test_custom_plan_unknown_workout(client, user_token):
    resp = client.post("/api/plans", headers=h(user_token), json={
        "name": "Bad", "items": [{"workout_id": 999, "day_of_week": 0}],
    })
    assert resp.status_code == 404
