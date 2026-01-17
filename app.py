import os
import sqlite3
from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    send_from_directory, flash
)

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.secret_key = "jarvis-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- FIXED PASSWORD ----------------
FIXED_PASSWORD = "jarvis@123"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
        """)
init_db()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == FIXED_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Wrong password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def login_required():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if login_required():
        return login_required()
    return render_template("dashboard.html")

# ---------------- NOTES ----------------
@app.route("/notes", methods=["GET", "POST"])
def notes():
    if login_required():
        return login_required()

    con = get_db()

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            con.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            con.commit()

    notes = con.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    return render_template("notes.html", notes=notes)

# ---------------- FILE UPLOAD ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if login_required():
        return login_required()

    if request.method == "POST":
        file = request.files.get("file")
        if file:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            flash("File uploaded successfully")

    files = os.listdir(UPLOAD_FOLDER)
    return render_template("files.html", files=files)

@app.route("/download/<filename>")
def download(filename):
    if login_required():
        return login_required()
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)