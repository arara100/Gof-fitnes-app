from app.repositories.user_repository import UserRepository
from app.services.errors import ServiceError

ROLES = ("user", "admin")


class UserAdminService:
    """Admin-only user management (Use Case: manage users)."""

    def __init__(self, users=None):
        self.users = users or UserRepository()

    def list(self):
        return sorted(self.users.list(), key=lambda u: u.id)

    def _get(self, user_id):
        user = self.users.get(user_id)
        if not user:
            raise ServiceError("User not found", 404)
        return user

    def set_role(self, acting_id, user_id, role):
        user = self._get(user_id)
        if user.id == int(acting_id):
            raise ServiceError("You cannot change your own role", 409)
        user.role = role
        self.users.commit()
        return user

    def delete(self, acting_id, user_id):
        user = self._get(user_id)
        if user.id == int(acting_id):
            raise ServiceError("You cannot delete yourself", 409)
        self.users.delete_with_dependents(user)
        self.users.commit()
