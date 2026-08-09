from datetime import datetime
from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.String(20), nullable=False)

    student_name = db.Column(db.String(100), nullable=False)

    year = db.Column(db.String(20))

    branch = db.Column(db.String(20))

    section = db.Column(db.String(10))

    teacher = db.Column(db.String(100))

    category = db.Column(db.String(100))

    language = db.Column(db.String(100))

    topic = db.Column(db.String(200))

    system_number = db.Column(db.String(20))

    remarks = db.Column(db.String(300))

    date = db.Column(db.Date, default=datetime.utcnow)

    time_in = db.Column(db.DateTime, default=datetime.utcnow)

    time_out = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Attendance {self.student_id}>"