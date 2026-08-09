from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
from datetime import datetime, timedelta, date

from app import db
from app.models import Attendance, Student

from io import BytesIO
from openpyxl import Workbook

attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/admin/attendance")
def attendance_list():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    records = Attendance.query.order_by(
        Attendance.time_in.desc()
    ).all()

    return render_template(
        "admin/attendance.html",
        records=records
    )


@attendance_bp.route("/student/attendance", methods=["GET", "POST"])
def student_attendance():

    if "student_id" not in session:
        return redirect(url_for("main.student_login"))

    student = Student.query.get(session["student_id"])

    if request.method == "POST":

        today = datetime.now().date()

        print("Student ID:", student.student_id)
        print("Today:", today)

        already_marked = Attendance.query.filter(
        Attendance.student_id == student.student_id,
        Attendance.date == today
        ).first()

        print("Already Marked:", already_marked)

        if already_marked:
            flash("You have already marked attendance today.", "warning")
            session.clear()
            return redirect(url_for("main.home"))

        attendance = Attendance(

            student_id=student.student_id,
            student_name=student.name,

            year=student.year,
            branch=student.branch,
            section=student.section,

            teacher=request.form["teacher"],

            category=request.form["category"],

            language=request.form["language"],

            topic=request.form["topic"],

            system_number=request.form["system_number"],

            remarks=request.form["remarks"],

            date=today,

            time_in=datetime.now()

        )

        db.session.add(attendance)
        db.session.commit()

        flash("Attendance Submitted Successfully!", "success")

        session.clear()

        return redirect(url_for("main.home"))

    return render_template(
        "student/attendance.html",
        student=student
    )



@attendance_bp.route("/admin/report", methods=["GET", "POST"])
def attendance_report():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    records = []

    if request.method == "POST":

        student_id = request.form["student_id"].strip()

        report_type = request.form["report_type"]

        today = datetime.now().date()

        query = Attendance.query.filter(
            Attendance.student_id == student_id
        )

        if report_type == "daily":

            query = query.filter(
                Attendance.date == today
            )

        elif report_type == "weekly":

            start_date = today - timedelta(days=7)

            query = query.filter(
                Attendance.date >= start_date
            )

        elif report_type == "monthly":

            start_date = today.replace(day=1)

            query = query.filter(
                Attendance.date >= start_date
            )

        records = query.order_by(
            Attendance.date.desc()
        ).all()

    return render_template(
        "admin/report.html",
        records=records
    )


@attendance_bp.route("/admin/report/export", methods=["POST"])
def export_report():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    student_id = request.form["student_id"].strip()
    report_type = request.form["report_type"]

    today = datetime.now().date()

    query = Attendance.query.filter(
        Attendance.student_id == student_id
    )

    if report_type == "daily":

        query = query.filter(
            Attendance.date == today
        )

    elif report_type == "weekly":

        start_date = today - timedelta(days=7)

        query = query.filter(
            Attendance.date >= start_date
        )

    elif report_type == "monthly":

        start_date = today.replace(day=1)

        query = query.filter(
            Attendance.date >= start_date
        )

    records = query.order_by(
        Attendance.date.desc()
    ).all()

    wb = Workbook()

    ws = wb.active

    ws.title = "Attendance Report"

    ws.append([
        "Date",
        "Student ID",
        "Student Name",
        "Teacher",
        "Language",
        "Topic",
        "System Number",
        "Remarks"
    ])

    for r in records:

        ws.append([
            str(r.date),
            r.student_id,
            r.student_name,
            r.teacher,
            r.language,
            r.topic,
            r.system_number,
            r.remarks
        ])

    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Attendance_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )