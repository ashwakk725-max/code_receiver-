from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from functools import wraps
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ---------------- SECURITY SETTINGS ----------------

app.secret_key = os.getenv("SECRET_KEY")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# ---------------- MONGODB CONNECTION ----------------

MONGO_URI = os.getenv("MONGO_URI")

mongo_client = MongoClient(MONGO_URI)

database = mongo_client["code_receiver"]

submissions_collection = database["submissions"]


# ---------------- PUBLIC PAGE ----------------

@app.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()

        if name and code:

            submissions_collection.insert_one({
                "name": name,
                "code": code,
                "submitted_at": datetime.now(timezone.utc)
            })

            message = "Code sent successfully!"

        else:

            message = "Please enter your name and code."

    return render_template(
        "index.html",
        message=message
    )


# ---------------- ADMIN PROTECTION ----------------

def admin_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        return function(*args, **kwargs)

    return decorated_function


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    error = ""

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(url_for("admin_dashboard"))

        else:

            error = "Invalid username or password."

    return render_template(
        "admin_login.html",
        error=error
    )


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    submissions = submissions_collection.find().sort("_id", -1)

    return render_template(
        "admin_dashboard.html",
        submissions=submissions
    )


# ---------------- ADMIN LOGOUT ----------------

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("admin_login"))


# ---------------- START SERVER ----------------

if __name__ == "__main__":
    app.run(debug=True)