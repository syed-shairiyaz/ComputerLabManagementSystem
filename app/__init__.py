from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # -----------------------------------------
    # DATABASE
    # -----------------------------------------

    db.init_app(app)


    # -----------------------------------------
    # IMPORT MODELS
    # -----------------------------------------

    from app.models import (
        Student,
        Admin,
        Teacher,
        Attendance,
        ComputerSystem,
        Category,
        WorkingDay,
        Announcement,
        AnnouncementResponse
    )


    # -----------------------------------------
    # CREATE DATABASE TABLES
    # -----------------------------------------

    with app.app_context():

        db.create_all()


        # -----------------------------------------
        # DEFAULT ADMIN
        # -----------------------------------------

        admin = Admin.query.filter_by(
            username="admin"
        ).first()


        if not admin:

            admin = Admin(
                username="admin",
                password="admin123",
                full_name="Administrator"
            )

            db.session.add(admin)

            db.session.commit()


    # -----------------------------------------
    # IMPORT ROUTES
    # -----------------------------------------

    from app.routes import (
        main,
        student_bp,
        teacher_bp,
        attendance_bp,
        computer_bp,
        announcement_bp
    )


    # -----------------------------------------
    # REGISTER BLUEPRINTS
    # -----------------------------------------

    app.register_blueprint(main)

    app.register_blueprint(student_bp)

    app.register_blueprint(teacher_bp)

    app.register_blueprint(attendance_bp)

    app.register_blueprint(computer_bp)

    app.register_blueprint(announcement_bp)


    return app