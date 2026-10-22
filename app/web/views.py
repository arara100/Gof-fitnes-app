"""Server-rendered pages. They contain no logic: every page talks to the REST API from JS."""
from flask import Blueprint, render_template

bp = Blueprint("web", __name__)

PAGES = {
    "/": ("dashboard.html", "Головна"),
    "/login": ("login.html", "Вхід"),
    "/workouts": ("workouts.html", "Тренування"),
    "/plans": ("plans.html", "Мої програми"),
    "/social": ("social.html", "Досягнення та челенджі"),
    "/reminders": ("reminders.html", "Нагадування"),
    "/profile": ("profile.html", "Профіль"),
    "/admin": ("admin.html", "Адмін-панель"),
}


def _make_view(template, title):
    def view():
        return render_template(template, title=title)

    return view


for path, (template, title) in PAGES.items():
    bp.add_url_rule(path, endpoint=template.replace(".html", ""), view_func=_make_view(template, title))
