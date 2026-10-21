from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User

CREDS = {"email": "u@example.com", "password": "secret1"}


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={**CREDS, "profile": {"age": 28, "gender": "male"}})
    assert resp.status_code == 201
    assert resp.get_json()["user"]["profile"]["age"] == 28
    login = client.post("/api/auth/login", json=CREDS)
    assert login.status_code == 200
    assert "access_token" in login.get_json()


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json=CREDS)
    assert client.post("/api/auth/register", json=CREDS).status_code == 409


def test_register_validation(client):
    resp = client.post("/api/auth/register", json={"email": "bad", "password": "1"})
    assert resp.status_code == 422


def test_login_wrong_password(client):
    client.post("/api/auth/register", json=CREDS)
    resp = client.post("/api/auth/login", json={**CREDS, "password": "wrong"})
    assert resp.status_code == 401


def test_profile_requires_token(client):
    assert client.get("/api/users/me").status_code == 401


def test_get_and_update_profile(client):
    token = client.post("/api/auth/register", json=CREDS).get_json()["access_token"]
    resp = client.put(
        "/api/users/me", json={"weight_kg": 72.5, "height_cm": 180, "goal": "endurance"},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    me = client.get("/api/users/me", headers=auth_header(token)).get_json()
    assert me["profile"]["weight_kg"] == 72.5 and me["profile"]["goal"] == "endurance"


def test_profile_invalid_value(client):
    token = client.post("/api/auth/register", json=CREDS).get_json()["access_token"]
    resp = client.put("/api/users/me", json={"age": 500}, headers=auth_header(token))
    assert resp.status_code == 422


def test_admin_required(app, client):
    from app.api.utils import admin_required

    @app.get("/api/_admin_probe")
    @admin_required
    def probe():
        return {"ok": True}

    user_token = client.post("/api/auth/register", json=CREDS).get_json()["access_token"]
    assert client.get("/api/_admin_probe", headers=auth_header(user_token)).status_code == 403

    db.session.add(User(email="admin@example.com", password_hash=generate_password_hash("pw1234", method="pbkdf2:sha256"), role="admin"))
    db.session.commit()
    admin_token = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "pw1234"}).get_json()["access_token"]
    assert client.get("/api/_admin_probe", headers=auth_header(admin_token)).get_json() == {"ok": True}
