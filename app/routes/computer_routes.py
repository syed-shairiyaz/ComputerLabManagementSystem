from flask import Blueprint, render_template, request, redirect, url_for, session

from app import db
from app.models import ComputerSystem

computer_bp = Blueprint("computer", __name__)


@computer_bp.route("/admin/computers")
def computers():

    if "admin_id" not in session:
       return redirect(url_for("main.admin_login"))

    computers = ComputerSystem.query.order_by(
        ComputerSystem.system_number
    ).all()

    return render_template(
        "admin/computers.html",
        computers=computers
    )


@computer_bp.route("/admin/computers/add", methods=["GET", "POST"])
def add_computer():

    if request.method == "POST":

        computer = ComputerSystem(
            system_number=request.form["system_number"],
            status=request.form["status"],
            issue=request.form["issue"],
            remarks=request.form["remarks"]
        )

        db.session.add(computer)
        db.session.commit()

        return redirect(url_for("computer.computers"))

    return render_template("admin/add_computer.html")


@computer_bp.route("/admin/computers/edit/<int:id>", methods=["GET", "POST"])
def edit_computer(id):

    computer = ComputerSystem.query.get_or_404(id)

    if request.method == "POST":

        computer.system_number = request.form["system_number"]
        computer.status = request.form["status"]
        computer.issue = request.form["issue"]
        computer.remarks = request.form["remarks"]

        db.session.commit()

        return redirect(url_for("computer.computers"))

    return render_template(
        "admin/edit_computer.html",
        computer=computer
    )


@computer_bp.route("/admin/computers/delete/<int:id>")
def delete_computer(id):

    computer = ComputerSystem.query.get_or_404(id)

    db.session.delete(computer)
    db.session.commit()

    return redirect(url_for("computer.computers"))