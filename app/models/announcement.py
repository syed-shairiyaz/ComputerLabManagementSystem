from app import db
from datetime import datetime


class Announcement(db.Model):

    __tablename__ = "announcements"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------
    # ANNOUNCEMENT CONTENT
    # -----------------------------------------

    title = db.Column(
        db.String(200),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        default="Normal"
    )

    status = db.Column(
        db.String(20),
        default="Published"
    )

    # -----------------------------------------
    # TARGETING
    # -----------------------------------------

    target_year = db.Column(
        db.String(50),
        nullable=True
    )

    target_branch = db.Column(
        db.String(50),
        nullable=True
    )

    target_section = db.Column(
        db.String(50),
        nullable=True
    )

    target_student_id = db.Column(
        db.String(50),
        nullable=True
    )

    # -----------------------------------------
    # ACTION SETTINGS
    # -----------------------------------------

    action_type = db.Column(
        db.String(30),
        default="None"
    )

    allow_response = db.Column(
        db.Boolean,
        default=False
    )

    # -----------------------------------------
    # DATES
    # -----------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    expires_at = db.Column(
        db.DateTime,
        nullable=True
    )

    # -----------------------------------------
    # ADMIN
    # -----------------------------------------

    created_by = db.Column(
        db.String(100),
        nullable=True
    )