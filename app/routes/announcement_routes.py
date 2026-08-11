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

    # -----------------------------------------
    # ADMIN LOGIN PROTECTION
    # -----------------------------------------

    if "admin_id" not in session:
        return redirect(
            url_for("main.admin_login")
        )

    # -----------------------------------------
    # POST REQUEST
    # -----------------------------------------

    if request.method == "POST":

        # -----------------------------------------
        # BASIC DETAILS
        # -----------------------------------------

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

        # -----------------------------------------
        # STUDENT TARGET
        #
        # all
        # 1
        # 2
        # 3
        # 4
        # -----------------------------------------

        target_year = request.form.get(
            "target_year",
            "all"
        ).strip()

        # -----------------------------------------
        # BRANCH TARGET
        #
        # all
        # CSE
        # CSE-CS
        # CSE-DS
        # AIML
        # EEE
        # ECE
        # -----------------------------------------

        target_branch = request.form.get(
            "target_branch",
            "all"
        ).strip()

        # -----------------------------------------
        # ALLOW STUDENT REPLY
        # -----------------------------------------

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
        # CREATE ANNOUNCEMENT
        # -----------------------------------------

        announcement = Announcement(

            title=title,

            message=message,

            priority=priority,

            status=status,

            target_year=(
                None
                if target_year == "all"
                else target_year
            ),

            target_branch=(
                None
                if target_branch == "all"
                else target_branch
            ),

            # These are no longer used
            target_section=None,

            target_student_id=None,

            # No separate action requirement now
            action_type="None",

            allow_response=allow_response,

            created_by=session.get(
                "admin_name"
            )
        )

        # -----------------------------------------
        # SAVE
        # -----------------------------------------

        db.session.add(
            announcement
        )

        db.session.commit()

        # -----------------------------------------
        # SUCCESS MESSAGE
        # -----------------------------------------

        flash(
            "Announcement created successfully!",
            "success"
        )

        return redirect(
            url_for(
                "announcement.announcements"
            )
        )

    # -----------------------------------------
    # SHOW CREATE PAGE
    # -----------------------------------------

    return render_template(
        "admin/create_announcement.html"
    )

# =========================================================
# STUDENT - ANNOUNCEMENTS
# =========================================================

@announcement_bp.route("/student/announcements")
def student_announcements():

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

    from app.models import Student

    student = Student.query.get(
        session["student_id"]
    )


    if not student:

        session.clear()

        return redirect(
            url_for("main.student_login")
        )


    # -----------------------------------------
    # GET ALL PUBLISHED ANNOUNCEMENTS
    # -----------------------------------------

    announcements = Announcement.query.filter_by(
        status="Published"
    ).order_by(
        Announcement.created_at.desc()
    ).all()


    # -----------------------------------------
    # FILTER ANNOUNCEMENTS
    # -----------------------------------------

    visible_announcements = []


    for announcement in announcements:

        # -------------------------------------
        # YEAR CHECK
        # -------------------------------------

        year_match = (

            announcement.target_year is None

            or str(
                announcement.target_year
            ) == str(
                student.year
            )
        )


        # -------------------------------------
        # BRANCH CHECK
        # -------------------------------------

        branch_match = (

            announcement.target_branch is None

            or announcement.target_branch.lower()
            == str(student.branch).lower()
        )


        # -------------------------------------
        # ADD IF BOTH MATCH
        # -------------------------------------

        if year_match and branch_match:

            visible_announcements.append(
                announcement
            )


    return render_template(
        "student/announcements.html",

        announcements=visible_announcements,

        student=student
    )

# =========================================================
# STUDENT - VIEW ANNOUNCEMENT
# =========================================================

@announcement_bp.route(
    "/student/announcements/<int:announcement_id>",
    methods=["GET", "POST"]
)
def student_announcement(announcement_id):

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

    from app.models import Student

    student = Student.query.get(
        session["student_id"]
    )


    if not student:

        session.clear()

        return redirect(
            url_for("main.student_login")
        )


    # -----------------------------------------
    # GET ANNOUNCEMENT
    # -----------------------------------------

    announcement = Announcement.query.get_or_404(
        announcement_id
    )


    # -----------------------------------------
    # CHECK YEAR
    # -----------------------------------------

    year_match = (

        announcement.target_year is None

        or str(
            announcement.target_year
        ) == str(
            student.year
        )
    )


    # -----------------------------------------
    # CHECK BRANCH
    # -----------------------------------------

    branch_match = (

        announcement.target_branch is None

        or announcement.target_branch.lower()
        == str(student.branch).lower()
    )


    # -----------------------------------------
    # BLOCK UNAUTHORIZED STUDENT
    # -----------------------------------------

    if not year_match or not branch_match:

        flash(
            "You are not allowed to view this announcement.",
            "danger"
        )

        return redirect(
            url_for(
                "announcement.student_announcements"
            )
        )


    # -----------------------------------------
    # REPLY
    # -----------------------------------------

    if request.method == "POST":

        if not announcement.allow_response:

            flash(
                "Replies are not allowed for this announcement.",
                "warning"
            )

            return redirect(
                url_for(
                    "announcement.student_announcement",
                    announcement_id=announcement.id
                )
            )


        reply = request.form.get(
            "reply",
            ""
        ).strip()


        if not reply:

            flash(
                "Please enter a reply.",
                "danger"
            )

            return redirect(
                url_for(
                    "announcement.student_announcement",
                    announcement_id=announcement.id
                )
            )


        # -------------------------------------
        # SAVE RESPONSE
        # -------------------------------------

        from app.models import AnnouncementResponse


        response = AnnouncementResponse(

            announcement_id=announcement.id,

            student_id=student.student_id,

            student_name=student.name,

            response=reply

        )


        db.session.add(response)

        db.session.commit()


        flash(
            "Your reply has been submitted successfully!",
            "success"
        )


        return redirect(
            url_for(
                "announcement.student_announcement",
                announcement_id=announcement.id
            )
        )


    # -----------------------------------------
    # GET EXISTING RESPONSES
    # -----------------------------------------

    from app.models import AnnouncementResponse


    responses = AnnouncementResponse.query.filter_by(

        announcement_id=announcement.id,

        student_id=student.student_id

    ).order_by(

        AnnouncementResponse.created_at.desc()

    ).all()


    return render_template(

        "student/announcement.html",

        announcement=announcement,

        student=student,

        responses=responses

    )