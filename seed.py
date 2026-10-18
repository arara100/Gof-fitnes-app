"""Fill the database with demo data: `python seed.py` (idempotent)."""
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.models import (
    Achievement, CardioWorkout, Challenge, Profile, StrengthWorkout, User, Workout, YogaWorkout,
)

WORKOUTS = [
    (CardioWorkout, "Біг підтюпцем", 30, "easy", 7.0),
    (CardioWorkout, "HIIT 20 хвилин", 20, "hard", 10.0),
    (CardioWorkout, "Велотренажер", 40, "medium", 6.8),
    (StrengthWorkout, "Базове тренування всього тіла", 45, "medium", 5.0),
    (StrengthWorkout, "Тренування верху тіла", 50, "hard", 6.0),
    (StrengthWorkout, "Присідання та випади", 35, "medium", 5.5),
    (YogaWorkout, "Ранкова йога", 25, "easy", 2.5),
    (YogaWorkout, "Віньяса-флоу", 45, "medium", 3.5),
]

ACHIEVEMENTS = [
    ("first_session", "Перше тренування", "sessions", 1),
    ("ten_sessions", "10 тренувань", "sessions", 10),
    ("burn_1000", "Спалено 1000 ккал", "calories", 1000),
    ("minutes_600", "10 годин активності", "minutes", 600),
]


def seed():
    if not User.query.filter_by(email="admin@fitness.local").first():
        admin = User(
            email="admin@fitness.local",
            password_hash=generate_password_hash("admin123", method="pbkdf2:sha256"),
            role="admin",
        )
        admin.profile = Profile(gender="male", age=30, weight_kg=80, height_cm=180, goal="endurance")
        db.session.add(admin)

    if Workout.query.count() == 0:
        for cls, title, minutes, difficulty, met in WORKOUTS:
            db.session.add(cls(title=title, duration_min=minutes, difficulty=difficulty, met=met))

    for code, title, metric, threshold in ACHIEVEMENTS:
        if not Achievement.query.filter_by(code=code).first():
            db.session.add(Achievement(code=code, title=title, metric=metric, threshold=threshold))

    if Challenge.query.count() == 0:
        today = date.today()
        db.session.add(
            Challenge(
                title="12 тренувань за місяць", metric="sessions", target=12,
                start_date=today, end_date=today + timedelta(days=30),
            )
        )
    db.session.commit()


if __name__ == "__main__":
    with create_app().app_context():
        seed()
        print("Seed done")
