from app import db


class ComputerSystem(db.Model):
    __tablename__ = "computer_systems"

    id = db.Column(db.Integer, primary_key=True)

    system_number = db.Column(db.String(20), unique=True, nullable=False)

    status = db.Column(db.String(30), default="Working")

    issue = db.Column(db.String(300))

    remarks = db.Column(db.String(300))

    def __repr__(self):
        return f"<Computer {self.system_number}>"