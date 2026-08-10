from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from app import db
from app.models import Student, Attendance


student_bp = Blueprint("student", __name__)


# =========================================================
# STUDENT MANAGEMENT
# =========================================================

@student_bp.route("/admin/students")
def students():

    # Admin login protection
    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    # -----------------------------------------
    # GET FILTER VALUES
    # -----------------------------------------

    selected_year = request.args.get("year", "").strip()
    selected_branch = request.args.get("branch", "").strip()
    search = request.args.get("search", "").strip()


    # -----------------------------------------
    # START QUERY
    # -----------------------------------------

    query = Student.query


    # -----------------------------------------
    # YEAR FILTER
    # -----------------------------------------

    if selected_year:

        query = query.filter(
            Student.year == selected_year
        )


    # -----------------------------------------
    # BRANCH FILTER
    # -----------------------------------------

    if selected_branch:

        query = query.filter(
            Student.branch == selected_branch
        )


    # -----------------------------------------
    # SEARCH STUDENT ID / NAME
    # -----------------------------------------

    if search:

        query = query.filter(
            (Student.student_id.ilike(f"%{search}%")) |
            (Student.name.ilike(f"%{search}%"))
        )


    # -----------------------------------------
    # GET STUDENTS
    # -----------------------------------------

    students = query.order_by(
        Student.student_id
    ).all()


    # -----------------------------------------
    # SEND DATA TO TEMPLATE
    # -----------------------------------------

    return render_template(
        "admin/students.html",

        students=students,

        selected_year=selected_year,

        selected_branch=selected_branch,

        search=search
    )


# =========================================================
# ADD STUDENT
# =========================================================

@student_bp.route("/admin/students/add", methods=["GET", "POST"])
def add_student():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))


    if request.method == "POST":

        student_id = request.form["student_id"].strip()

        name = request.form["name"].strip()

        password = request.form["password"]

        year = request.form["year"]

        branch = request.form["branch"]

        section = request.form["section"]

        status = request.form["status"]


        # -----------------------------------------
        # CHECK DUPLICATE STUDENT ID
        # -----------------------------------------

        existing_student = Student.query.filter_by(
            student_id=student_id
        ).first()


        if existing_student:

            flash(
                "Student ID already exists. Please use a different Student ID.",
                "danger"
            )

            return redirect(
                url_for("student.add_student")
            )


        # -----------------------------------------
        # CREATE STUDENT
        # -----------------------------------------

        student = Student(

            student_id=student_id,

            name=name,

            password=password,

            year=year,

            branch=branch,

            section=section,

            status=status
        )


        db.session.add(student)

        db.session.commit()


        flash(
            "Student added successfully!",
            "success"
        )


        return redirect(
            url_for("student.students")
        )


    return render_template(
        "admin/add_student.html"
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@student_bp.route(
    "/admin/students/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit_student(id):

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))


    student = Student.query.get_or_404(id)


    if request.method == "POST":

        student.name = request.form["name"]

        student.password = request.form["password"]

        student.year = request.form["year"]

        student.branch = request.form["branch"]

        student.section = request.form["section"]

        student.status = request.form["status"]


        db.session.commit()


        flash(
            "Student updated successfully!",
            "success"
        )


        return redirect(
            url_for("student.students")
        )


    return render_template(
        "admin/edit_student.html",

        student=student
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@student_bp.route(
    "/admin/students/delete/<int:id>"
)
def delete_student(id):

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))


    student = Student.query.get_or_404(id)


    db.session.delete(student)

    db.session.commit()


    flash(
        "Student deleted successfully!",
        "success"
    )


    return redirect(
        url_for("student.students")
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@student_bp.route("/student/dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect(
            url_for("main.student_login")
        )


    return render_template(
        "student/dashboard.html",

        name=session["student_name"]
    )


# =========================================================
# ADMIN SEARCH STUDENT + ATTENDANCE
# =========================================================

@student_bp.route(
    "/admin/student/search",
    methods=["GET", "POST"]
)
def search_student():

    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )


    student = None

    records = []


    if request.method == "POST":

        keyword = request.form["keyword"].strip()


        student = Student.query.filter(

            (Student.student_id == keyword) |

            (Student.name.ilike(
                f"%{keyword}%"
            ))

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