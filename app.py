from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
from functools import wraps

app = Flask(__name__)

# Change this to a long random secret before putting the website online
app.secret_key = "change-this-to-a-random-secret-key"

# Admin login
ADMIN_USERNAME = "ASHWAK"
ADMIN_PASSWORD = "EXAM"


def get_database_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ASHWAK",
        database="code_receiver"
    )


# ---------------- PUBLIC PAGE ----------------

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()

        if name and code:
            connection = get_database_connection()
            cursor = connection.cursor()

            cursor.execute(
                "INSERT INTO submissions (name, code) VALUES (%s, %s)",
                (name, code)
            )

            connection.commit()

            cursor.close()
            connection.close()

            message = "Code sent successfully!"

        else:
            message = "Please enter your name and code."

    return render_template("index.html", message=message)


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

    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, code, submitted_at
        FROM submissions
        ORDER BY id DESC
    """)

    submissions = cursor.fetchall()

    cursor.close()
    connection.close()

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