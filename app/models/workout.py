from app.extensions import db


class Workout(db.Model):
    """Single-table inheritance: the `type` column picks the subclass."""

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration_min = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default="medium")
    met = db.Column(db.Float, nullable=False, default=5.0)  # metabolic equivalent

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "workout"}


class CardioWorkout(Workout):
    __mapper_args__ = {"polymorphic_identity": "cardio"}


class StrengthWorkout(Workout):
    __mapper_args__ = {"polymorphic_identity": "strength"}


class YogaWorkout(Workout):
    __mapper_args__ = {"polymorphic_identity": "yoga"}


class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    goal = db.Column(db.String(30))

    user = db.relationship("User", back_populates="plans")
    items = db.relationship(
        "PlanItem", back_populates="plan", cascade="all, delete-orphan", order_by="PlanItem.position"
    )


class PlanItem(db.Model):
    __tablename__ = "plan_items"

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("workout_plans.id"), nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0 = Monday
    position = db.Column(db.Integer, nullable=False, default=0)

    plan = db.relationship("WorkoutPlan", back_populates="items")
    workout = db.relationship("Workout")


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False, index=True)
    performed_at = db.Column(db.DateTime, nullable=False)
    duration_min = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Float, nullable=False, default=0)

    user = db.relationship("User", back_populates="sessions")
    workout = db.relationship("Workout")
