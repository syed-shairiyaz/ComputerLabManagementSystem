from app import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    department = db.Column(db.String(100))

    status = db.Column(db.String(20), default="Active")

    def __repr__(self):
        return f"<Teacher {self.name}>"