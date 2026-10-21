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

    from app.api import auth, users, workouts

    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(workouts.bp)

    @app.errorhandler(ServiceError)
    def handle_service_error(err):
        return jsonify(error=err.message), err.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify(error="Validation failed", details=err.messages), 422

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    return app
