from app import db


class WorkingDay(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    date = db.Column(
        db.Date,
        unique=True,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Working",
        nullable=False
    )

    remarks = db.Column(
        db.String(200)
    )

    def __repr__(self):
        return f"<WorkingDay {self.date}>"