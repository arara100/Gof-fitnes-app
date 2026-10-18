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

    user = db.relationship("User", back_populates="reminders")
