from app.extensions import db


class Repository:
    """Generic persistence gateway; services depend on this, not on SQLAlchemy queries."""

    model = None

    def get(self, entity_id):
        return db.session.get(self.model, entity_id)

    def list(self):
        return self.model.query.all()

    def add(self, entity):
        db.session.add(entity)
        return entity

    def delete(self, entity):
        db.session.delete(entity)

    def commit(self):
        db.session.commit()
