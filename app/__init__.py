from flask import Flask, jsonify
from marshmallow import ValidationError

from config import Config
from app.extensions import db, jwt, migrate
from app.services.errors import ServiceError


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    from app import models  # noqa: F401  (register models for migrations)

    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.api import admin_users, auth, plans, reminders, reports, sessions, social, stats, users, workouts

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(workouts.bp)
    app.register_blueprint(plans.bp)
    app.register_blueprint(sessions.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(social.bp)
    app.register_blueprint(reminders.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(admin_users.bp)

    from app.web import views

    app.register_blueprint(views.bp)

    from app.patterns.observers import register_observers

    register_observers()

    @app.errorhandler(ServiceError)
    def handle_service_error(err):
        return jsonify(error=err.message), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify(error="Validation failed", details=err.messages), 422

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    if app.config.get("SCHEDULER_ENABLED"):
        import os

        # With the debug reloader only the child process (WERKZEUG_RUN_MAIN) should run jobs.
        if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            from app.scheduler import start_scheduler

            start_scheduler(app)

    return app
