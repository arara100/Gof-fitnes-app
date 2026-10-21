from marshmallow import Schema, fields, validate

GENDERS = ("male", "female", "other")
GOALS = ("lose_weight", "gain_muscle", "endurance")


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
