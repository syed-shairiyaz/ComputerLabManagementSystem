from flask import Blueprint, render_template, request, redirect, session, url_for

from app import db
from app.models import Student

student_bp = Blueprint("student", __name__)


@student_bp.route("/admin/students")
def students():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    students = Student.query.order_by(Student.student_id).all()

    return render_template(
        "admin/students.html",
        students=students
    )


@student_bp.route("/admin/students/add", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        student = Student(
            student_id=request.form["student_id"],
            name=request.form["name"],
            password=request.form["password"],
            year=request.form["year"],
            branch=request.form["branch"],
            section=request.form["section"],
            status=request.form["status"]
        )

        db.session.add(student)
        db.session.commit()

        return redirect(url_for("student.students"))

    return render_template("admin/add_student.html")


@student_bp.route("/admin/students/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":

        student.name = request.form["name"]
        student.password = request.form["password"]
        student.year = request.form["year"]
        student.branch = request.form["branch"]
        student.section = request.form["section"]
        student.status = request.form["status"]

        db.session.commit()

        return redirect(url_for("student.students"))

    return render_template(
        "admin/edit_student.html",
        student=student
    )


@student_bp.route("/admin/students/delete/<int:id>")
def delete_student(id):

    student = Student.query.get_or_404(id)

    db.session.delete(student)

    db.session.commit()

    return redirect(url_for("student.students"))


@student_bp.route("/student/dashboard")
def student_dashboard():

    from flask import session, redirect, url_for

    if "student_id" not in session:
        return redirect(url_for("main.student_login"))

    return render_template(
        "student/dashboard.html",
        name=session["student_name"]
    )

from app.models import Attendance

@student_bp.route("/admin/student/search", methods=["GET", "POST"])
def search_student():

    student = None
    records = []

    if request.method == "POST":

        keyword = request.form["keyword"]

        student = Student.query.filter(
            (Student.student_id == keyword) |
            (Student.name.ilike(f"%{keyword}%"))
        ).first()

        if student:

            records = Attendance.query.filter_by(
                student_id=student.student_id
            ).order_by(
                Attendance.time_in.desc()
            ).all()

    return render_template(
        "admin/search_student.html",
        student=student,
        records=records
    )