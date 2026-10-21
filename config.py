import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://fitness:fitness@localhost:5432/fitness",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret")


class TestConfig(Config):
    TESTING = True
    JWT_SECRET_KEY = "test-secret-key-at-least-32-bytes-long"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
