from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from app import db
from app.models import Announcement


announcement_bp = Blueprint(
    "announcement",
    __name__
)


# =========================================================
# ADMIN - ANNOUNCEMENT LIST
# =========================================================

@announcement_bp.route("/admin/announcements")
def announcements():

    # Admin login protection
    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )

    announcements = Announcement.query.order_by(
        Announcement.created_at.desc()
    ).all()

    return render_template(
        "admin/announcements.html",
        announcements=announcements
    )


# =========================================================
# ADMIN - CREATE ANNOUNCEMENT
# =========================================================

@announcement_bp.route(
    "/admin/announcements/create",
    methods=["GET", "POST"]
)
def create_announcement():

    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        priority = request.form.get(
            "priority",
            "Normal"
        )

        status = request.form.get(
            "status",
            "Published"
        )

        target_year = request.form.get(
            "target_year",
            ""
        ).strip()

        target_branch = request.form.get(
            "target_branch",
            ""
        ).strip()

        target_section = request.form.get(
            "target_section",
            ""
        ).strip()

        target_student_id = request.form.get(
            "target_student_id",
            ""
        ).strip()

        action_type = request.form.get(
            "action_type",
            "None"
        )

        allow_response = (
            request.form.get("allow_response")
            == "yes"
        )


        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not title:

            flash(
                "Announcement title is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "announcement.create_announcement"
                )
            )


        if not message:

            flash(
                "Announcement message is required.",
                "danger"
            )

            return redirect(
                url_for(
                    "announcement.create_announcement"
                )
            )


        # -----------------------------------------
        # CREATE
        # -----------------------------------------

        announcement = Announcement(

            title=title,

            message=message,

            priority=priority,

            status=status,

            target_year=target_year or None,

            target_branch=target_branch or None,

            target_section=target_section or None,

            target_student_id=target_student_id or None,

            action_type=action_type,

            allow_response=allow_response,

            created_by=session.get(
                "admin_name"
            )
        )


        db.session.add(announcement)

        db.session.commit()


        flash(
            "Announcement created successfully!",
            "success"
        )


        return redirect(
            url_for(
                "announcement.announcements"
            )
        )


    return render_template(
        "admin/create_announcement.html"
    )


# =========================================================
# ADMIN - VIEW ANNOUNCEMENT
# =========================================================

@announcement_bp.route(
    "/admin/announcements/<int:announcement_id>"
)
def view_announcement(announcement_id):

    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )

    announcement = Announcement.query.get_or_404(
        announcement_id
    )

    return render_template(
        "admin/view_announcement.html",
        announcement=announcement
    )


# =========================================================
# ADMIN - EDIT ANNOUNCEMENT
# =========================================================

@announcement_bp.route(
    "/admin/announcements/<int:announcement_id>/edit",
    methods=["GET", "POST"]
)
def edit_announcement(announcement_id):

    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )

    announcement = Announcement.query.get_or_404(
        announcement_id
    )


    if request.method == "POST":

        announcement.title = request.form.get(
            "title",
            ""
        ).strip()

        announcement.message = request.form.get(
            "message",
            ""
        ).strip()

        announcement.priority = request.form.get(
            "priority",
            "Normal"
        )

        announcement.status = request.form.get(
            "status",
            "Published"
        )

        announcement.target_year = (
            request.form.get(
                "target_year",
                ""
            ).strip()
            or None
        )

        announcement.target_branch = (
            request.form.get(
                "target_branch",
                ""
            ).strip()
            or None
        )

        announcement.target_section = (
            request.form.get(
                "target_section",
                ""
            ).strip()
            or None
        )

        announcement.target_student_id = (
            request.form.get(
                "target_student_id",
                ""
            ).strip()
            or None
        )

        announcement.action_type = request.form.get(
            "action_type",
            "None"
        )

        announcement.allow_response = (
            request.form.get("allow_response")
            == "yes"
        )


        db.session.commit()


        flash(
            "Announcement updated successfully!",
            "success"
        )


        return redirect(
            url_for(
                "announcement.announcements"
            )
        )


    return render_template(
        "admin/edit_announcement.html",
        announcement=announcement
    )