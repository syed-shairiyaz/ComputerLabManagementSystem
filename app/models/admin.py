from app import db


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    full_name = db.Column(db.String(100), nullable=False)

    status = db.Column(db.String(20), default="Active")

    def __repr__(self):
        return f"<Admin {self.username}>"