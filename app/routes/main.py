from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date, datetime

from app import db

from app.models import (
    Student,
    Teacher,
    Attendance,
    ComputerSystem,
    Admin,
    WorkingDay
)


main = Blueprint("main", __name__)


# =========================================================
# HOME PAGE
# =========================================================

@main.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@main.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:

        return redirect(
            url_for("main.admin_login")
        )

    total_students = Student.query.count()

    total_teachers = Teacher.query.count()

    today_attendance = Attendance.query.filter_by(
        date=date.today()
    ).count()

    working_systems = ComputerSystem.query.filter_by(
        status="Working"
    ).count()

    non_working_systems = ComputerSystem.query.filter_by(
        status="Not Working"
    ).count()

    recent_attendance = Attendance.query.order_by(
        Attendance.time_in.desc()
    ).limit(10).all()

    return render_template(
        "admin/dashboard.html",

        total_students=total_students,

        total_teachers=total_teachers,

        today_attendance=today_attendance,

        working_systems=working_systems,

        non_working_systems=non_working_systems,

        recent_attendance=recent_attendance
    )


# =========================================================
# LOGOUT
# =========================================================

@main.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("main.home")
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@main.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form["username"].strip()

        password = request.form["password"]

        admin = Admin.query.filter_by(
            username=username,
            password=password
        ).first()

        if admin:

            session["admin_id"] = admin.id

            session["admin_name"] = admin.username

            return redirect(
                url_for("main.admin_dashboard")
            )

        flash(
            "Invalid Username or Password",
            "danger"
        )

    return render_template(
        "auth/admin_login.html"
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

@main.route(
    "/student/login",
    methods=["GET", "POST"]
)
def student_login():

    if request.method == "POST":

        student_id = request.form["student_id"].strip()

        password = request.form["password"]

        student = Student.query.filter_by(
            student_id=student_id,
            password=password
        ).first()

        if student:

            session["student_id"] = student.id

            session["student_name"] = student.name

            return redirect(
                url_for("student.student_dashboard")
            )

        flash(
            "Invalid Student ID or Password",
            "danger"
        )

    return render_template(
        "auth/student_login.html"
    )


# =========================================================
# ADMIN SETTINGS
# =========================================================

@main.route(
    "/admin/settings",
    methods=["GET", "POST"]
)
def admin_settings():

    # -----------------------------------------------------
    # ADMIN LOGIN PROTECTION
    # -----------------------------------------------------

    if "admin_id" not in session:

        return redirect(
            url_for("main.admin_login")
        )


    # -----------------------------------------------------
    # GET CURRENT ADMIN
    # -----------------------------------------------------

    admin = Admin.query.get(
        session["admin_id"]
    )


    if not admin:

        session.clear()

        return redirect(
            url_for("main.admin_login")
        )


    # -----------------------------------------------------
    # UPDATE ADMIN SETTINGS
    # -----------------------------------------------------

    if request.method == "POST":

        current_password = request.form[
            "current_password"
        ]

        new_username = request.form[
            "new_username"
        ].strip()

        new_password = request.form[
            "new_password"
        ]

        confirm_password = request.form[
            "confirm_password"
        ]


        # =================================================
        # CHECK CURRENT PASSWORD
        # =================================================

        if admin.password != current_password:

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("main.admin_settings")
            )


        # =================================================
        # CHECK USERNAME
        # =================================================

        if not new_username:

            flash(
                "Username cannot be empty.",
                "danger"
            )

            return redirect(
                url_for("main.admin_settings")
            )


        # -------------------------------------------------
        # CHECK DUPLICATE USERNAME
        # -------------------------------------------------

        existing_admin = Admin.query.filter(
            Admin.username == new_username,
            Admin.id != admin.id
        ).first()


        if existing_admin:

            flash(
                "This username is already taken.",
                "danger"
            )

            return redirect(
                url_for("main.admin_settings")
            )


        # =================================================
        # CHECK PASSWORD
        # =================================================

        # Password is optional.
        # If empty, keep the existing password.

        if new_password:

            if len(new_password) < 6:

                flash(
                    "New password must contain at least 6 characters.",
                    "warning"
                )

                return redirect(
                    url_for("main.admin_settings")
                )


            if new_password != confirm_password:

                flash(
                    "New passwords do not match.",
                    "danger"
                )

                return redirect(
                    url_for("main.admin_settings")
                )


            # Update password
            admin.password = new_password


        # =================================================
        # UPDATE USERNAME
        # =================================================

        admin.username = new_username


        # =================================================
        # SAVE CHANGES
        # =================================================

        db.session.commit()


        # Update current session
        session["admin_name"] = admin.username


        flash(
            "Admin settings updated successfully!",
            "success"
        )


        return redirect(
            url_for("main.admin_settings")
        )


    # =====================================================
    # DISPLAY SETTINGS PAGE
    # =====================================================

    return render_template(
        "admin/settings.html",
        admin=admin
    )


# =========================================================
# WORKING DAYS
# =========================================================

@main.route(
    "/admin/working-days",
    methods=["GET", "POST"]
)
def working_days():

    # Admin only

    if "admin_id" not in session:

        return redirect(
            url_for("main.admin_login")
        )


    # -----------------------------------------------------
    # ADD WORKING DAY
    # -----------------------------------------------------

    if request.method == "POST":

        date_string = request.form["date"]

        remarks = request.form.get(
            "remarks",
            ""
        ).strip()


        selected_date = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        ).date()


        # -------------------------------------------------
        # CHECK DUPLICATE DATE
        # -------------------------------------------------

        existing_day = WorkingDay.query.filter_by(
            date=selected_date
        ).first()


        if existing_day:

            flash(
                "This date is already added.",
                "warning"
            )

            return redirect(
                url_for("main.working_days")
            )


        # -------------------------------------------------
        # CREATE WORKING DAY
        # -------------------------------------------------

        working_day = WorkingDay(

            date=selected_date,

            status="Working",

            remarks=remarks
        )


        db.session.add(
            working_day
        )

        db.session.commit()


        flash(
            "Working day added successfully!",
            "success"
        )


        return redirect(
            url_for("main.working_days")
        )


    # -----------------------------------------------------
    # SHOW WORKING DAYS
    # -----------------------------------------------------

    days = WorkingDay.query.order_by(
        WorkingDay.date.desc()
    ).all()


    return render_template(
        "admin/working_days.html",
        days=days
    )