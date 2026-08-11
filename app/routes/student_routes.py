from flask import Blueprint, render_template, request, redirect, session, url_for, flash

from app import db
from app.models import Student, Attendance, Announcement, AnnouncementResponse


student_bp = Blueprint("student", __name__)


# =========================================================
# ADMIN - STUDENT MANAGEMENT
# =========================================================

@student_bp.route("/admin/students")
def students():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    selected_year = request.args.get("year", "").strip()
    selected_branch = request.args.get("branch", "").strip()
    search = request.args.get("search", "").strip()

    query = Student.query

    # Year filter
    if selected_year:
        query = query.filter(
            Student.year == selected_year
        )

    # Branch filter
    if selected_branch:
        query = query.filter(
            Student.branch == selected_branch
        )

    # Search ID / Name
    if search:
        query = query.filter(
            (Student.student_id.ilike(f"%{search}%")) |
            (Student.name.ilike(f"%{search}%"))
        )

    students = query.order_by(
        Student.student_id
    ).all()

    return render_template(
        "admin/students.html",
        students=students,
        selected_year=selected_year,
        selected_branch=selected_branch,
        search=search
    )


# =========================================================
# ADMIN - ADD STUDENT
# =========================================================

@student_bp.route(
    "/admin/students/add",
    methods=["GET", "POST"]
)
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

        # Check duplicate Student ID
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
# ADMIN - EDIT STUDENT
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
# ADMIN - DELETE STUDENT
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

    # -----------------------------------------
    # STUDENT LOGIN PROTECTION
    # -----------------------------------------

    if "student_id" not in session:
        return redirect(
            url_for("main.student_login")
        )

    # -----------------------------------------
    # GET LOGGED-IN STUDENT
    # -----------------------------------------

    student = Student.query.get_or_404(
        session["student_id"]
    )

    # -----------------------------------------
    # GET ANNOUNCEMENTS
    # -----------------------------------------

    announcements = Announcement.query.filter(

        Announcement.status == "Published",

        (
            # All students
            (
                Announcement.target_year.is_(None)
            )
            |
            (
                Announcement.target_year == ""
            )
        )
        |
        (
            Announcement.target_year == student.year
        ),

        (
            # All branches
            (
                Announcement.target_branch.is_(None)
            )
            |
            (
                Announcement.target_branch == ""
            )
        )
        |
        (
            Announcement.target_branch == student.branch
        )

    ).order_by(
        Announcement.created_at.desc()
    ).all()

    # -----------------------------------------
    # STUDENT DASHBOARD
    # -----------------------------------------

    return render_template(
        "student/dashboard.html",

        name=student.name,

        student=student,

        announcements=announcements
    )

# =========================================================
# PUBLIC STUDENT SEARCH
# =========================================================
# Students / visitors can use this.
# NO ADMIN LOGIN REQUIRED.
#
# Only basic student information is shown.
# Attendance records remain private.
# =========================================================

@student_bp.route(
    "/student/search",
    methods=["GET", "POST"]
)
def search_student():

    student = None

    working_days = 0
    present_days = 0
    absent_days = 0
    attendance_percentage = 0

    if request.method == "POST":

        keyword = request.form.get(
            "keyword",
            ""
        ).strip()

        if keyword:

            student = Student.query.filter(
                (Student.student_id.ilike(
                    f"%{keyword}%"
                )) |
                (Student.name.ilike(
                    f"%{keyword}%"
                ))
            ).first()

            # --------------------------------
            # ATTENDANCE SUMMARY
            # --------------------------------

            if student:

                # Currently we use the number
                # of attendance dates as present days.
                present_days = Attendance.query.filter_by(
                    student_id=student.student_id
                ).count()

                # Temporary working-days calculation
                working_days = present_days

                absent_days = 0

                if working_days > 0:

                    attendance_percentage = (
                        present_days / working_days
                    ) * 100

    return render_template(
        "student/search_student.html",

        student=student,

        working_days=working_days,

        present_days=present_days,

        absent_days=absent_days,

        attendance_percentage=attendance_percentage
    )

# =========================================================
# ADMIN - SEARCH STUDENT + ATTENDANCE
# =========================================================
# This is different from the public search.
#
# Admin can see the student's attendance history.
# =========================================================

@student_bp.route(
    "/admin/student/search",
    methods=["GET", "POST"]
)
def admin_search_student():

    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )

    student = None

    records = []

    if request.method == "POST":

        keyword = request.form.get(
            "keyword",
            ""
        ).strip()

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
# =========================================================
# STUDENT - REPLY TO ANNOUNCEMENT
# =========================================================

@student_bp.route(
    "/student/announcement/<int:announcement_id>/respond",
    methods=["POST"]
)
def respond_to_announcement(announcement_id):

    # -----------------------------------------
    # STUDENT LOGIN PROTECTION
    # -----------------------------------------

    if "student_id" not in session:
        return redirect(
            url_for("main.student_login")
        )

    # -----------------------------------------
    # GET STUDENT
    # -----------------------------------------

    student = Student.query.get_or_404(
        session["student_id"]
    )

    # -----------------------------------------
    # GET ANNOUNCEMENT
    # -----------------------------------------

    announcement = Announcement.query.get_or_404(
        announcement_id
    )

    # -----------------------------------------
    # CHECK REPLY PERMISSION
    # -----------------------------------------

    if not announcement.allow_response:

        flash(
            "Replies are not allowed for this announcement.",
            "warning"
        )

        return redirect(
            url_for("student.student_dashboard")
        )

    # -----------------------------------------
    # GET RESPONSE
    # -----------------------------------------

    response_text = request.form.get(
        "response",
        ""
    ).strip()

    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------

    if not response_text:

        flash(
            "Please enter your response.",
            "danger"
        )

        return redirect(
            url_for("student.student_dashboard")
        )

    # -----------------------------------------
    # CHECK EXISTING RESPONSE
    # -----------------------------------------

    existing_response = AnnouncementResponse.query.filter_by(
        announcement_id=announcement.id,
        student_id=student.student_id
    ).first()

    # -----------------------------------------
    # UPDATE EXISTING RESPONSE
    # -----------------------------------------

    if existing_response:

        existing_response.response_text = response_text

        existing_response.replied = True

        db.session.commit()

        flash(
            "Your response has been updated successfully.",
            "success"
        )

        return redirect(
            url_for("student.student_dashboard")
        )

    # -----------------------------------------
    # CREATE NEW RESPONSE
    # -----------------------------------------

    response = AnnouncementResponse(

        announcement_id=announcement.id,

        student_id=student.student_id,

        response_text=response_text,

        replied=True

    )

    db.session.add(response)

    db.session.commit()

    # -----------------------------------------
    # SUCCESS
    # -----------------------------------------

    flash(
        "Your response has been submitted successfully.",
        "success"
    )

    return redirect(
        url_for("student.student_dashboard")
    )