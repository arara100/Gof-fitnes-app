from app.models import User


def h(token):
    return {"Authorization": f"Bearer {token}"}


def test_list_requires_admin(client, user_token, admin_token):
    assert client.get("/api/admin/users", headers=h(user_token)).status_code == 403
    emails = [u["email"] for u in client.get("/api/admin/users", headers=h(admin_token)).get_json()]
    assert emails == ["u@example.com", "admin@example.com"] or set(emails) == {"u@example.com", "admin@example.com"}


def test_change_role_and_self_protection(client, user_token, admin_token):
    users = client.get("/api/admin/users", headers=h(admin_token)).get_json()
    uid = next(u["id"] for u in users if u["email"] == "u@example.com")
    aid = next(u["id"] for u in users if u["email"] == "admin@example.com")
    ok = client.put(f"/api/admin/users/{uid}", headers=h(admin_token), json={"role": "admin"})
    assert ok.get_json()["role"] == "admin"
    assert client.put(f"/api/admin/users/{aid}", headers=h(admin_token), json={"role": "user"}).status_code == 409
    assert client.put(f"/api/admin/users/{uid}", headers=h(admin_token), json={"role": "root"}).status_code == 422
    assert client.delete(f"/api/admin/users/{aid}", headers=h(admin_token)).status_code == 409


def test_delete_user_with_data(client, user_token, admin_token):
    client.post("/api/reminders", headers=h(user_token), json={"time": "07:30"})
    from datetime import datetime
    from app.services.reminder_service import ReminderService
    ReminderService().dispatch_due(datetime(2026, 10, 19, 7, 30))  # creates a notification
    uid = User.query.filter_by(email="u@example.com").one().id
    assert client.delete(f"/api/admin/users/{uid}", headers=h(admin_token)).status_code == 204
    assert User.query.filter_by(email="u@example.com").first() is None
    assert client.delete("/api/admin/users/999", headers=h(admin_token)).status_code == 404
