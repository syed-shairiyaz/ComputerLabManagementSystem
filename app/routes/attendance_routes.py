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

    if not student:
        session.clear()
        return redirect(url_for("main.student_login"))

    if request.method == "POST":

        today = datetime.now().date()

        # --------------------------------
        # PREVENT MULTIPLE ATTENDANCE
        # --------------------------------

        already_marked = Attendance.query.filter(
            Attendance.student_id == student.student_id,
            Attendance.date == today
        ).first()

        if already_marked:

            flash(
                "You have already marked attendance today.",
                "warning"
            )

            session.clear()

            return redirect(url_for("main.home"))

        # --------------------------------
        # CREATE ATTENDANCE
        # --------------------------------

        attendance = Attendance(

            # Student details from database
            student_id=student.student_id,
            student_name=student.name,

            year=student.year,
            branch=student.branch,
            section=student.section,

            # Topic / system / remarks from student form
            topic=request.form["topic"],

            system_number=request.form["system_number"],

            remarks=request.form["remarks"],

            # Automatically generated
            date=today,

            time_in=datetime.now()

        )

        db.session.add(attendance)

        db.session.commit()

        flash(
            "Attendance Submitted Successfully!",
            "success"
        )

        # Logout student after attendance
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

    selected_group = ""
    selected_report_type = "daily"
    student_id = ""

    if request.method == "POST":

        student_id = request.form.get("student_id", "").strip()
        selected_report_type = request.form.get("report_type", "daily")
        selected_group = request.form.get("group", "").strip()

        today = datetime.now().date()

        # Start with all attendance records
        query = Attendance.query

        # --------------------------------
        # STUDENT FILTER
        # --------------------------------
        if student_id:
            query = query.filter(
                Attendance.student_id == student_id
            )

        # --------------------------------
        # GROUP / BRANCH FILTER
        # --------------------------------
        if selected_group:
            query = query.filter(
                Attendance.branch == selected_group
            )

        # --------------------------------
        # DATE FILTER
        # --------------------------------
        if selected_report_type == "daily":

            query = query.filter(
                Attendance.date == today
            )

        elif selected_report_type == "weekly":

            start_date = today - timedelta(days=7)

            query = query.filter(
                Attendance.date >= start_date
            )

        elif selected_report_type == "monthly":

            start_date = today.replace(day=1)

            query = query.filter(
                Attendance.date >= start_date
            )

        records = query.order_by(
            Attendance.date.desc(),
            Attendance.time_in.desc()
        ).all()

    return render_template(
        "admin/report.html",
        records=records,
        selected_group=selected_group,
        selected_report_type=selected_report_type,
        student_id=student_id
    )

@attendance_bp.route("/admin/report/export", methods=["POST"])
def export_report():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    student_id = request.form.get("student_id", "").strip()
    report_type = request.form.get("report_type", "daily")
    selected_group = request.form.get("group", "").strip()

    today = datetime.now().date()

    # --------------------------------
    # START QUERY
    # --------------------------------

    query = Attendance.query

    # --------------------------------
    # STUDENT FILTER
    # --------------------------------

    if student_id:
        query = query.filter(
            Attendance.student_id == student_id
        )

    # --------------------------------
    # GROUP FILTER
    # --------------------------------

    if selected_group:
        query = query.filter(
            Attendance.branch == selected_group
        )

    # --------------------------------
    # DATE FILTER
    # --------------------------------

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
        Attendance.date.desc(),
        Attendance.time_in.desc()
    ).all()

    # --------------------------------
    # CREATE EXCEL FILE
    # --------------------------------

    wb = Workbook()

    # Remove default sheet
    default_ws = wb.active
    wb.remove(default_ws)

    # --------------------------------
    # GROUP RECORDS
    # --------------------------------

    groups = {}

    for r in records:

        branch = r.branch or "Unknown"

        if branch not in groups:
            groups[branch] = []

        groups[branch].append(r)

    # --------------------------------
    # IF NO RECORDS
    # --------------------------------

    if not groups:

        ws = wb.create_sheet("No Data")

        ws.append([
            "No attendance records found"
        ])

    else:

        # --------------------------------
        # CREATE SHEETS GROUP-WISE
        # --------------------------------

        for branch, branch_records in groups.items():

            # Excel sheet names cannot exceed 31 characters
            sheet_name = branch[:31]

            ws = wb.create_sheet(sheet_name)

            # Header
            ws.append([
                "Date",
                "Student ID",
                "Student Name",
                "Year",
                "Branch",
                "Section",
                "Teacher",
                "Category",
                "Language",
                "Topic",
                "System Number",
                "Remarks",
                "Time In"
            ])

            # Data
            for r in branch_records:

                ws.append([
                    str(r.date),
                    r.student_id,
                    r.student_name,
                    r.year,
                    r.branch,
                    r.section,
                    r.teacher,
                    r.category,
                    r.language,
                    r.topic,
                    r.system_number,
                    r.remarks,
                    str(r.time_in)
                ])

            # --------------------------------
            # MAKE COLUMNS EASIER TO READ
            # --------------------------------

            for column in ws.columns:

                max_length = 0

                column_letter = column[0].column_letter

                for cell in column:

                    if cell.value is not None:

                        length = len(str(cell.value))

                        if length > max_length:
                            max_length = length

                ws.column_dimensions[column_letter].width = min(
                    max_length + 2,
                    30
                )

            # Freeze header
            ws.freeze_panes = "A2"

    # --------------------------------
    # SAVE FILE
    # --------------------------------

    output = BytesIO()

    wb.save(output)

    output.seek(0)

    # --------------------------------
    # FILE NAME
    # --------------------------------

    if selected_group:
        filename = f"{selected_group}_Attendance_Report.xlsx"
    else:
        filename = "All_Groups_Attendance_Report.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )