from datetime import date, datetime

import pytest

from app import create_app
from app.extensions import db
from app.models import (
    CardioWorkout, Challenge, ChallengeParticipation, PlanItem, Profile, User, Workout,
    WorkoutPlan, WorkoutSession, YogaWorkout,
)
from config import TestConfig


@pytest.fixture
def app_ctx():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def test_user_profile_relationship(app_ctx):
    user = User(email="a@b.c", password_hash="x")
    user.profile = Profile(gender="female", age=25, weight_kg=60, height_cm=168)
    db.session.add(user)
    db.session.commit()
    assert User.query.one().profile.age == 25


def test_workout_polymorphism(app_ctx):
    db.session.add_all([
        CardioWorkout(title="Run", duration_min=30), YogaWorkout(title="Flow", duration_min=20),
    ])
    db.session.commit()
    types = {type(w).__name__ for w in Workout.query.all()}
    assert types == {"CardioWorkout", "YogaWorkout"}


def test_plan_session_and_challenge(app_ctx):
    user = User(email="a@b.c", password_hash="x")
    workout = CardioWorkout(title="Run", duration_min=30)
    plan = WorkoutPlan(user=user, name="Plan", items=[PlanItem(workout=workout, day_of_week=0)])
    session = WorkoutSession(
        user=user, workout=workout, performed_at=datetime.utcnow(), duration_min=30, calories=250
    )
    challenge = Challenge(
        title="C", metric="sessions", target=5, start_date=date(2026, 1, 1), end_date=date(2026, 2, 1)
    )
    part = ChallengeParticipation(user=user, challenge=challenge)
    db.session.add_all([plan, session, part])
    db.session.commit()
    assert user.plans[0].items[0].workout.title == "Run"
    assert user.sessions[0].calories == 250
    assert challenge.participations[0].progress == 0
