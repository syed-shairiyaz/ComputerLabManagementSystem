from app import db
from datetime import datetime


class AnnouncementResponse(db.Model):

    __tablename__ = "announcement_responses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------
    # RELATION
    # -----------------------------------------

    announcement_id = db.Column(
        db.Integer,
        db.ForeignKey("announcements.id"),
        nullable=False
    )

    student_id = db.Column(
        db.String(50),
        nullable=False
    )

    # -----------------------------------------
    # TRACKING
    # -----------------------------------------

    seen = db.Column(
        db.Boolean,
        default=False
    )

    seen_at = db.Column(
        db.DateTime,
        nullable=True
    )

    acknowledged = db.Column(
        db.Boolean,
        default=False
    )

    reacted = db.Column(
        db.Boolean,
        default=False
    )

    replied = db.Column(
        db.Boolean,
        default=False
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    # -----------------------------------------
    # STUDENT RESPONSE
    # -----------------------------------------

    response_text = db.Column(
        db.Text,
        nullable=True
    )

    reason = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------------------
    # DATE
    # -----------------------------------------

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )