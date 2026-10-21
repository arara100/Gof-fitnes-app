from datetime import datetime

from app.extensions import db


class WeightEntry(db.Model):
    __tablename__ = "weight_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)

    user = db.relationship("User", back_populates="weight_entries")


class Reminder(db.Model):
    __tablename__ = "reminders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    time = db.Column(db.Time, nullable=False)
    days = db.Column(db.String(20), nullable=False, default="0,1,2,3,4,5,6")
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    last_sent_date = db.Column(db.Date)  # prevents sending twice on the same day

    user = db.relationship("User", back_populates="reminders")


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    reminder_id = db.Column(db.Integer, db.ForeignKey("reminders.id", ondelete="SET NULL"))
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
