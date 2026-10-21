from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import Profile, User
from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError

PROFILE_FIELDS = ("gender", "age", "weight_kg", "height_cm", "goal")
HASH_METHOD = "pbkdf2:sha256"


class AuthService:
    def __init__(self, users=None):
        self.users = users or UserRepository()

    def register(self, email, password, profile_data=None):
        email = email.strip().lower()
        if self.users.get_by_email(email):
            raise ServiceError("Email already registered", 409)
        user = User(
            email=email,
            password_hash=generate_password_hash(password, method=HASH_METHOD),
            role="user",
        )
        user.profile = Profile(**(profile_data or {}))
        self.users.add(user)
        self.users.commit()
        return user

    def login(self, email, password):
        user = self.users.get_by_email(email.strip().lower())
        if not user or not check_password_hash(user.password_hash, password):
            raise ServiceError("Invalid email or password", 401)
        return self.issue_token(user)

    @staticmethod
    def issue_token(user):
        return create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    def get_user(self, user_id):
        user = self.users.get(int(user_id))
        if not user:
            raise ServiceError("User not found", 404)
        return user

    def update_profile(self, user_id, data):
        user = self.get_user(user_id)
        if user.profile is None:
            user.profile = Profile()
        for field in PROFILE_FIELDS:
            if field in data:
                setattr(user.profile, field, data[field])
        self.users.commit()
        return user
