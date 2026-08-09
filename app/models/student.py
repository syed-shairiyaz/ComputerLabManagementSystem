from app import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.String(20), unique=True, nullable=False)

    name = db.Column(db.String(100), nullable=False)

    password = db.Column(db.String(200), nullable=False)

    year = db.Column(db.String(20), nullable=False)

    branch = db.Column(db.String(20), nullable=False)

    section = db.Column(db.String(10), nullable=False)

    status = db.Column(db.String(20), default="Active")

    def __repr__(self):
        return f"<Student {self.student_id}>"