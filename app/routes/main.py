from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date

from app.models import Student, Teacher, Attendance, ComputerSystem, Admin

main = Blueprint("main", __name__)


# ---------------- HOME ----------------

@main.route("/")
def home():
    return render_template("index.html")


# ---------------- ADMIN ----------------

@main.route("/admin/dashboard")
def admin_dashboard():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

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

@main.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("main.home"))

@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        admin = Admin.query.filter_by(
            username=username,
            password=password
        ).first()

        if admin:

            session["admin_id"] = admin.id
            session["admin_name"] = admin.username

            return redirect(url_for("main.admin_dashboard"))

        flash("Invalid Username or Password", "danger")

    return render_template("auth/admin_login.html")



# ---------------- STUDENT ----------------

@main.route("/student/login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        student_id = request.form["student_id"]
        password = request.form["password"]

        student = Student.query.filter_by(
            student_id=student_id,
            password=password
        ).first()

        if student:

            session["student_id"] = student.id
            session["student_name"] = student.name

            return redirect(url_for("student.student_dashboard"))

        flash("Invalid Student ID or Password", "danger")

    return render_template("auth/student_login.html")



