from app.extensions import db


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    metric = db.Column(db.String(30), nullable=False)  # sessions | calories | minutes
    threshold = db.Column(db.Float, nullable=False)


class UserAchievement(db.Model):
    __tablename__ = "user_achievements"
    __table_args__ = (db.UniqueConstraint("user_id", "achievement_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey("achievements.id"), nullable=False)
    earned_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", back_populates="achievements")
    achievement = db.relationship("Achievement")


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    metric = db.Column(db.String(30), nullable=False)  # sessions | calories | minutes
    target = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)

    participations = db.relationship(
        "ChallengeParticipation", back_populates="challenge", cascade="all, delete-orphan"
    )


class ChallengeParticipation(db.Model):
    __tablename__ = "challenge_participations"
    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    progress = db.Column(db.Float, nullable=False, default=0)

    user = db.relationship("User", back_populates="participations")
    challenge = db.relationship("Challenge", back_populates="participations")
