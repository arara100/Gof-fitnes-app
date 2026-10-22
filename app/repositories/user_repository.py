from app.models import User
from app.repositories.base import Repository


class UserRepository(Repository):
    model = User

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def delete_with_dependents(self, user):
        from app.extensions import db
        from app.models import Notification

        Notification.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
