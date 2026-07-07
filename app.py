from flask import Flask, render_template, request, redirect, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ZahraSecretKey"

# ---------------------- Database ----------------------
def get_db():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn

# جدول کاربران
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()
conn.close()

# جدول کارها
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS todolist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    onvan TEXT,
    vaziat TEXT,
    category TEXT DEFAULT 'عمومی',
    priority TEXT DEFAULT 'معمولی',
    user_id INTEGER
)
""")
conn.commit()
conn.close()

# ---------------------- Routes ----------------------
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM todolist WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("index.html", items=rows, username=session["username"])


# ---------------------- Signup ----------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         (username, password))
            conn.commit()
            flash("ثبت‌نام با موفقیت انجام شد!", "success")
            return redirect("/login")
        except:
            flash("این نام کاربری قبلاً ثبت شده!", "danger")
        finally:
            conn.close()

    return render_template("signup.html")


# ---------------------- Login ----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("ورود موفق!", "success")
            return redirect("/")
        else:
            flash("نام کاربری یا رمز اشتباه است!", "danger")

    return render_template("login.html")


# ---------------------- Logout ----------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("با موفقیت خارج شدید!", "info")
    return redirect("/login")


# ---------------------- Add Task ----------------------
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form["title"]
    category = request.form["category"]
    priority = request.form["priority"]

    conn = get_db()
    conn.execute("""
        INSERT INTO todolist (onvan, vaziat, category, priority, user_id)
        VALUES (?, ?, ?, ?, ?)
    """, (title, "[❌]", category, priority, session["user_id"]))
    conn.commit()
    conn.close()

    flash("کار با موفقیت اضافه شد!", "success")
    return redirect("/")


# ---------------------- Toggle Task ----------------------
@app.route("/toggle/<int:id>")
def toggle(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    row = conn.execute("SELECT vaziat FROM todolist WHERE id=? AND user_id=?",
                       (id, session["user_id"])).fetchone()

    if not row:
        flash("این کار متعلق به شما نیست!", "danger")
        return redirect("/")

    new_state = "[✔️]" if row["vaziat"] == "[❌]" else "[❌]"
    conn.execute("UPDATE todolist SET vaziat=? WHERE id=?", (new_state, id))
    conn.commit()
    conn.close()

    flash("وضعیت کار تغییر کرد!", "info")
    return redirect("/")


# ---------------------- Delete Task ----------------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    conn.execute("DELETE FROM todolist WHERE id=? AND user_id=?",
                 (id, session["user_id"]))
    conn.commit()
    conn.close()

    flash("کار حذف شد!", "danger")
    return redirect("/")


# ---------------------- Run ----------------------
app.run(debug=True)
