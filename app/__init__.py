from flask import Flask, jsonify

from config import Config
from app.extensions import db, jwt, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    from app import models  # noqa: F401  (register models for migrations)

    migrate.init_app(app, db)
    jwt.init_app(app)

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    return app
