import pytest

from app import create_app
from app.extensions import db
from config import TestConfig


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_token(client):
    resp = client.post("/api/auth/register", json={"email": "u@example.com", "password": "secret1"})
    return resp.get_json()["access_token"]


@pytest.fixture
def admin_token(client):
    from werkzeug.security import generate_password_hash

    from app.extensions import db
    from app.models import User

    db.session.add(User(
        email="admin@example.com",
        password_hash=generate_password_hash("adminpw1", method="pbkdf2:sha256"),
        role="admin",
    ))
    db.session.commit()
    resp = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "adminpw1"})
    return resp.get_json()["access_token"]
