from app.models import User
from app.repositories.base import Repository


class UserRepository(Repository):
    model = User

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()
