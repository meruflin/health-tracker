import os
import re
import uuid
from datetime import date
from functools import wraps
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
SQL_DIR = BASE_DIR / "sql"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "development-key-change-me")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


# ---------- DATABASE ----------

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "health_tracker"),
    )


def load_query(filename, query_name):
    """Read one named SQL query from a .sql file."""
    path = SQL_DIR / filename
    content = path.read_text(encoding="utf-8")

    pattern = rf"--\s*name:\s*{re.escape(query_name)}\s*\n(.*?)(?=--\s*name:|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise ValueError(f"Query '{query_name}' not found in {filename}")

    return match.group(1).strip()


def execute_query(filename, query_name, params=(), fetch=None):
    """
    fetch='one' returns one row.
    fetch='all' returns all rows.
    fetch=None executes a change and commits it.
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(load_query(filename, query_name), params)

        if fetch == "one":
            return cursor.fetchone()

        if fetch == "all":
            return cursor.fetchall()

        connection.commit()
        return cursor.lastrowid
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


# ---------- AUTHENTICATION ----------

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or len(password) < 8:
            flash("Enter your name, email, and a password of at least 8 characters.", "danger")
            return render_template("register.html")

        try:
            existing = execute_query(
                "auth.sql", "find_user_by_email", (email,), "one"
            )
            if existing:
                flash("That email is already registered.", "warning")
                return render_template("register.html")

            password_hash = generate_password_hash(password)
            execute_query(
                "auth.sql", "register_user",
                (name, email, password_hash)
            )
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))

        except mysql.connector.Error:
            app.logger.exception("Registration database error")
            flash("Could not create your account. Check your database setup.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        try:
            user = execute_query(
                "auth.sql", "find_user_by_email", (email,), "one"
            )

            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                return redirect(url_for("dashboard"))

            flash("Incorrect email or password.", "danger")

        except mysql.connector.Error:
            app.logger.exception("Login database error")
            flash("Could not connect to the database.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ---------- DASHBOARD ----------

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]

    counts = {
        "records": execute_query(
            "dashboard.sql", "records_count", (user_id,), "one"
        )["total"],
        "medicines": execute_query(
            "dashboard.sql", "medicines_count", (user_id,), "one"
        )["total"],
        "appointments": execute_query(
            "dashboard.sql", "appointments_count", (user_id,), "one"
        )["total"],
        "metrics": execute_query(
            "dashboard.sql", "metrics_count", (user_id,), "one"
        )["total"],
    }

    appointments = execute_query(
        "dashboard.sql", "upcoming_appointments", (user_id,), "all"
    )
    metrics = execute_query(
        "dashboard.sql", "recent_metrics", (user_id,), "all"
    )

    return render_template(
        "dashboard.html",
        counts=counts,
        appointments=appointments,
        metrics=metrics,
    )


# ---------- MEDICAL RECORDS ----------

@app.route("/records", methods=["GET", "POST"])
@login_required
def records():
    user_id = session["user_id"]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        record_type = request.form.get("record_type", "").strip()
        record_date = request.form.get("record_date", "")
        notes = request.form.get("notes", "").strip()

        if title and record_type and record_date:
            execute_query(
                "records.sql", "add_record",
                (user_id, title, record_type, record_date, notes)
            )
            flash("Medical record added.", "success")
            return redirect(url_for("records"))

        flash("Please complete the required fields.", "danger")

    items = execute_query(
        "records.sql", "list_records", (user_id,), "all"
    )
    return render_template("records.html", items=items, today=date.today().isoformat())


@app.route("/records/delete/<int:record_id>", methods=["POST"])
@login_required
def delete_record(record_id):
    execute_query(
        "records.sql", "delete_record",
        (record_id, session["user_id"])
    )
    flash("Medical record deleted.", "success")
    return redirect(url_for("records"))


# ---------- MEDICINES ----------

@app.route("/medicines", methods=["GET", "POST"])
@login_required
def medicines():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("medicine_name", "").strip()
        dosage = request.form.get("dosage", "").strip()
        schedule_time = request.form.get("schedule_time", "")
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date") or None
        instructions = request.form.get("instructions", "").strip()

        if name and schedule_time and start_date:
            execute_query(
                "medicines.sql", "add_medicine",
                (user_id, name, dosage, schedule_time,
                 start_date, end_date, instructions)
            )
            flash("Medicine schedule added.", "success")
            return redirect(url_for("medicines"))

        flash("Medicine name, time, and start date are required.", "danger")

    items = execute_query(
        "medicines.sql", "list_medicines", (user_id,), "all"
    )
    logs = execute_query(
        "medicines.sql", "medicine_logs_today", (user_id,), "all"
    )
    log_map = {item["medicine_id"]: item["status"] for item in logs}

    return render_template(
        "medicines.html", items=items, log_map=log_map,
        today=date.today().isoformat()
    )


@app.route("/medicines/log/<int:medicine_id>", methods=["POST"])
@login_required
def log_medicine(medicine_id):
    status = request.form.get("status")
    if status not in {"Taken", "Missed"}:
        abort(400)

    execute_query(
        "medicines.sql", "log_medicine",
        (session["user_id"], date.today(), status,
         medicine_id, session["user_id"])
    )
    flash(f"Medicine marked as {status.lower()}.", "success")
    return redirect(url_for("medicines"))


@app.route("/medicines/delete/<int:medicine_id>", methods=["POST"])
@login_required
def delete_medicine(medicine_id):
    execute_query(
        "medicines.sql", "delete_medicine",
        (medicine_id, session["user_id"])
    )
    flash("Medicine schedule deleted.", "success")
    return redirect(url_for("medicines"))


# ---------- APPOINTMENTS ----------

@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    user_id = session["user_id"]

    if request.method == "POST":
        doctor = request.form.get("doctor_name", "").strip()
        appointment_date = request.form.get("appointment_date", "")
        reason = request.form.get("reason", "").strip()

        if doctor and appointment_date:
            execute_query(
                "appointments.sql", "add_appointment",
                (user_id, doctor, appointment_date, reason)
            )
            flash("Appointment added.", "success")
            return redirect(url_for("appointments"))

        flash("Doctor name and appointment date are required.", "danger")

    items = execute_query(
        "appointments.sql", "list_appointments", (user_id,), "all"
    )
    return render_template("appointments.html", items=items)


@app.route("/appointments/complete/<int:appointment_id>", methods=["POST"])
@login_required
def complete_appointment(appointment_id):
    execute_query(
        "appointments.sql", "complete_appointment",
        (appointment_id, session["user_id"])
    )
    flash("Appointment marked as completed.", "success")
    return redirect(url_for("appointments"))


@app.route("/appointments/delete/<int:appointment_id>", methods=["POST"])
@login_required
def delete_appointment(appointment_id):
    execute_query(
        "appointments.sql", "delete_appointment",
        (appointment_id, session["user_id"])
    )
    flash("Appointment deleted.", "success")
    return redirect(url_for("appointments"))


# ---------- VACCINATIONS ----------

@app.route("/vaccinations", methods=["GET", "POST"])
@login_required
def vaccinations():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("vaccine_name", "").strip()
        dose_date = request.form.get("dose_date") or None
        next_due_date = request.form.get("next_due_date") or None
        notes = request.form.get("notes", "").strip()

        if name:
            execute_query(
                "vaccinations.sql", "add_vaccination",
                (user_id, name, dose_date, next_due_date, notes)
            )
            flash("Vaccination record added.", "success")
            return redirect(url_for("vaccinations"))

        flash("Vaccine name is required.", "danger")

    items = execute_query(
        "vaccinations.sql", "list_vaccinations", (user_id,), "all"
    )
    return render_template("vaccinations.html", items=items)


@app.route("/vaccinations/delete/<int:vaccine_id>", methods=["POST"])
@login_required
def delete_vaccination(vaccine_id):
    execute_query(
        "vaccinations.sql", "delete_vaccination",
        (vaccine_id, session["user_id"])
    )
    flash("Vaccination record deleted.", "success")
    return redirect(url_for("vaccinations"))


# ---------- HEALTH METRICS ----------

@app.route("/metrics", methods=["GET", "POST"])
@login_required
def metrics():
    user_id = session["user_id"]

    if request.method == "POST":
        metric_type = request.form.get("metric_type", "")
        value = request.form.get("value", "").strip()
        unit = request.form.get("unit", "").strip()
        notes = request.form.get("notes", "").strip()

        if metric_type not in {"Weight", "Blood Pressure", "Blood Sugar"}:
            flash("Choose a valid metric type.", "danger")
        elif value:
            execute_query(
                "metrics.sql", "add_metric",
                (user_id, metric_type, value, unit, notes)
            )
            flash("Health metric recorded.", "success")
            return redirect(url_for("metrics"))
        else:
            flash("Enter a metric value.", "danger")

    items = execute_query(
        "metrics.sql", "list_metrics", (user_id,), "all"
    )
    chart_items = execute_query(
        "metrics.sql", "chart_metrics", (user_id,), "all"
    )

    chart_data = [
        {
            "type": item["metric_type"],
            "value": item["value"],
            "unit": item["unit"],
            "date": item["recorded_at"].strftime("%Y-%m-%d %H:%M"),
        }
        for item in chart_items
    ]

    return render_template(
        "metrics.html", items=items, chart_data=chart_data
    )


# ---------- REPORT UPLOADS ----------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/reports", methods=["GET", "POST"])
@login_required
def reports():
    user_id = session["user_id"]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        uploaded = request.files.get("report_file")

        if not title or not uploaded or not uploaded.filename:
            flash("Provide a title and choose a file.", "danger")
        elif not allowed_file(uploaded.filename):
            flash("Only PDF, PNG, JPG, and JPEG files are allowed.", "danger")
        else:
            original = secure_filename(uploaded.filename)
            extension = original.rsplit(".", 1)[1].lower()
            stored = f"{uuid.uuid4().hex}.{extension}"
            uploaded.save(UPLOAD_DIR / stored)

            try:
                execute_query(
                    "profile.sql", "add_report",
                    (user_id, title, original, stored)
                )
                flash("Report uploaded successfully.", "success")
                return redirect(url_for("reports"))
            except Exception:
                (UPLOAD_DIR / stored).unlink(missing_ok=True)
                raise

    items = execute_query(
        "profile.sql", "list_reports", (user_id,), "all"
    )
    return render_template("reports.html", items=items)


@app.route("/reports/download/<int:report_id>")
@login_required
def download_report(report_id):
    report = execute_query(
        "profile.sql", "get_report",
        (report_id, session["user_id"]), "one"
    )
    if not report:
        abort(404)

    return send_from_directory(
        UPLOAD_DIR,
        report["stored_filename"],
        as_attachment=True,
        download_name=report["original_filename"],
    )


@app.route("/reports/delete/<int:report_id>", methods=["POST"])
@login_required
def delete_report(report_id):
    report = execute_query(
        "profile.sql", "get_report",
        (report_id, session["user_id"]), "one"
    )

    if report:
        execute_query(
            "profile.sql", "delete_report",
            (report_id, session["user_id"])
        )
        (UPLOAD_DIR / report["stored_filename"]).unlink(missing_ok=True)
        flash("Report deleted.", "success")

    return redirect(url_for("reports"))


# ---------- PROFILE ----------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip() or None
        dob = request.form.get("date_of_birth") or None

        if name:
            execute_query(
                "auth.sql", "update_profile",
                (name, phone, dob, user_id)
            )
            session["user_name"] = name
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))

        flash("Name is required.", "danger")

    user = execute_query(
        "auth.sql", "get_user", (user_id,), "one"
    )
    return render_template("profile.html", user=user)


@app.route("/profile/delete", methods=["POST"])
@login_required
def delete_account():
    user_id = session["user_id"]

    reports_list = execute_query(
        "profile.sql", "delete_user_reports", (user_id,), "all"
    )

    # Delete the database account and related records first.
    execute_query("auth.sql", "delete_user", (user_id,))

    # Remove that account's uploaded files from disk.
    for report in reports_list:
        (UPLOAD_DIR / report["stored_filename"]).unlink(missing_ok=True)

    session.clear()
    flash("Your account and associated records have been deleted.", "success")
    return redirect(url_for("login"))


@app.errorhandler(413)
def file_too_large(error):
    flash("The file is too large. The maximum upload size is 10 MB.", "danger")
    return redirect(url_for("reports"))


if __name__ == "__main__":
    app.run(debug=True)