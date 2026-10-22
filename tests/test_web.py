import pytest

PAGES = ["/", "/login", "/workouts", "/plans", "/social", "/reminders", "/profile", "/admin"]


@pytest.mark.parametrize("path", PAGES)
def test_page_renders(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    assert b"FitTrack" in resp.data and b"app.js" in resp.data


def test_static_assets(client):
    assert client.get("/static/js/app.js").status_code == 200
    assert client.get("/static/css/style.css").status_code == 200
