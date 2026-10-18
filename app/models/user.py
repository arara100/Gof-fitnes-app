from datetime import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    profile = db.relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    plans = db.relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")
    sessions = db.relationship("WorkoutSession", back_populates="user", cascade="all, delete-orphan")
    weight_entries = db.relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    reminders = db.relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    achievements = db.relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    participations = db.relationship(
        "ChallengeParticipation", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def is_admin(self):
        return self.role == "admin"


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    goal = db.Column(db.String(30))  # lose_weight | gain_muscle | endurance

    user = db.relationship("User", back_populates="profile")
