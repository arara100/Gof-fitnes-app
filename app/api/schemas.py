from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from app.patterns.plan_strategy import GOALS

GENDERS = ("male", "female", "other")


class ProfileSchema(Schema):
    gender = fields.String(validate=validate.OneOf(GENDERS))
    age = fields.Integer(validate=validate.Range(min=5, max=120))
    weight_kg = fields.Float(validate=validate.Range(min=20, max=400))
    height_cm = fields.Float(validate=validate.Range(min=50, max=260))
    goal = fields.String(validate=validate.OneOf(GOALS))


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=128))
    profile = fields.Nested(ProfileSchema)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


def serialize_user(user):
    profile = user.profile
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "profile": {f: getattr(profile, f) for f in ("gender", "age", "weight_kg", "height_cm", "goal")}
        if profile else None,
    }


DIFFICULTIES = ("easy", "medium", "hard")


class WorkoutCreateSchema(Schema):
    type = fields.String(required=True, validate=validate.OneOf(("cardio", "strength", "yoga")))
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(allow_none=True)
    duration_min = fields.Integer(required=True, validate=validate.Range(min=1, max=600))
    difficulty = fields.String(validate=validate.OneOf(DIFFICULTIES))
    met = fields.Float(validate=validate.Range(min=1, max=25))


class WorkoutUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=120))
    description = fields.String(allow_none=True)
    duration_min = fields.Integer(validate=validate.Range(min=1, max=600))
    difficulty = fields.String(validate=validate.OneOf(DIFFICULTIES))
    met = fields.Float(validate=validate.Range(min=1, max=25))


def serialize_workout(w):
    return {
        "id": w.id, "type": w.type, "title": w.title, "description": w.description,
        "duration_min": w.duration_min, "difficulty": w.difficulty, "met": w.met,
    }


class PlanItemSchema(Schema):
    workout_id = fields.Integer(required=True)
    day_of_week = fields.Integer(required=True, validate=validate.Range(min=0, max=6))


class PlanCreateSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    goal = fields.String(validate=validate.OneOf(GOALS))
    items = fields.List(fields.Nested(PlanItemSchema), required=True, validate=validate.Length(min=1))


class PlanGenerateSchema(Schema):
    name = fields.String(validate=validate.Length(min=1, max=120))
    goal = fields.String(validate=validate.OneOf(GOALS))


def serialize_plan(plan, entries=None):
    data = {"id": plan.id, "name": plan.name, "goal": plan.goal}
    if entries is not None:
        data["entries"] = [
            {"day": e.day, "title": e.title, "duration_min": e.duration_min,
             "kind": e.kind, "workout_id": e.workout_id}
            for e in entries
        ]
    return data


class SessionCreateSchema(Schema):
    workout_id = fields.Integer(required=True)
    duration_min = fields.Integer(validate=validate.Range(min=1, max=600))
    performed_at = fields.DateTime()


class SessionQuerySchema(Schema):
    date_from = fields.DateTime(data_key="from")
    date_to = fields.DateTime(data_key="to")


def serialize_session(s):
    return {
        "id": s.id, "workout_id": s.workout_id, "workout_title": s.workout.title,
        "type": s.workout.type, "performed_at": s.performed_at.isoformat(),
        "duration_min": s.duration_min, "calories": s.calories,
    }


METRICS = ("sessions", "calories", "minutes")


class WeightSchema(Schema):
    weight_kg = fields.Float(required=True, validate=validate.Range(min=20, max=400))
    date = fields.Date()


class AchievementSchema(Schema):
    code = fields.String(required=True, validate=validate.Length(min=1, max=50))
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(allow_none=True)
    metric = fields.String(required=True, validate=validate.OneOf(METRICS))
    threshold = fields.Float(required=True, validate=validate.Range(min=0))


class AchievementUpdateSchema(Schema):
    code = fields.String(validate=validate.Length(min=1, max=50))
    title = fields.String(validate=validate.Length(min=1, max=120))
    description = fields.String(allow_none=True)
    metric = fields.String(validate=validate.OneOf(METRICS))
    threshold = fields.Float(validate=validate.Range(min=0))


class ChallengeSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=120))
    description = fields.String(allow_none=True)
    metric = fields.String(required=True, validate=validate.OneOf(METRICS))
    target = fields.Float(required=True, validate=validate.Range(min=1))
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)

    @validates_schema
    def check_dates(self, data, **kwargs):
        if data["end_date"] < data["start_date"]:
            raise ValidationError("end_date must not be before start_date", "end_date")


class ChallengeUpdateSchema(Schema):
    title = fields.String(validate=validate.Length(min=1, max=120))
    description = fields.String(allow_none=True)
    metric = fields.String(validate=validate.OneOf(METRICS))
    target = fields.Float(validate=validate.Range(min=1))
    start_date = fields.Date()
    end_date = fields.Date()


def serialize_achievement(a, earned_at=None):
    return {
        "id": a.id, "code": a.code, "title": a.title, "description": a.description,
        "metric": a.metric, "threshold": a.threshold,
        "earned": earned_at is not None,
        "earned_at": earned_at.isoformat() if earned_at else None,
    }


def serialize_challenge(c, status, participation=None):
    data = {
        "id": c.id, "title": c.title, "description": c.description, "metric": c.metric,
        "target": c.target, "start_date": c.start_date.isoformat(),
        "end_date": c.end_date.isoformat(), "status": status, "joined": participation is not None,
    }
    if participation is not None:
        data["progress"] = participation.progress
        data["completed"] = participation.progress >= c.target
    return data


class ReminderSchema(Schema):
    time = fields.Time(required=True)
    days = fields.List(fields.Integer(validate=validate.Range(min=0, max=6)),
                       load_default=[0, 1, 2, 3, 4, 5, 6], validate=validate.Length(min=1))
    enabled = fields.Boolean(load_default=True)


class ReminderUpdateSchema(Schema):
    time = fields.Time()
    days = fields.List(fields.Integer(validate=validate.Range(min=0, max=6)), validate=validate.Length(min=1))
    enabled = fields.Boolean()


def serialize_reminder(r):
    return {
        "id": r.id, "time": r.time.strftime("%H:%M"),
        "days": [int(d) for d in r.days.split(",") if d != ""], "enabled": r.enabled,
    }


def serialize_notification(n):
    return {
        "id": n.id, "message": n.message, "is_read": n.is_read,
        "created_at": n.created_at.isoformat(), "reminder_id": n.reminder_id,
    }
