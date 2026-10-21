from marshmallow import Schema, fields, validate

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
