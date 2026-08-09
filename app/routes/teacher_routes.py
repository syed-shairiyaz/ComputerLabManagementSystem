from flask import Blueprint, render_template, request, redirect, url_for, session

from app import db
from app.models import Teacher

teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.route("/admin/teachers")
def teachers():

    if "admin_id" not in session:
        return redirect(url_for("main.admin_login"))

    teachers = Teacher.query.order_by(Teacher.name).all()

    return render_template(
        "admin/teachers.html",
        teachers=teachers
    )


@teacher_bp.route("/admin/teachers/add", methods=["GET", "POST"])
def add_teacher():

    if request.method == "POST":

        teacher = Teacher(

            name=request.form["name"],

            department=request.form["department"],

            status=request.form["status"]

        )

        db.session.add(teacher)

        db.session.commit()

        return redirect(url_for("teacher.teachers"))

    return render_template("admin/add_teacher.html")


@teacher_bp.route("/admin/teachers/edit/<int:id>", methods=["GET", "POST"])
def edit_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    if request.method == "POST":

        teacher.name = request.form["name"]
        teacher.department = request.form["department"]
        teacher.status = request.form["status"]

        db.session.commit()

        return redirect(url_for("teacher.teachers"))

    return render_template(
        "admin/edit_teacher.html",
        teacher=teacher
    )


@teacher_bp.route("/admin/teachers/delete/<int:id>")
def delete_teacher(id):

    teacher = Teacher.query.get_or_404(id)

    db.session.delete(teacher)

    db.session.commit()

    return redirect(url_for("teacher.teachers"))