from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import pymysql
# import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_very_secret_key_999'

# ==========================
# DB接続（Railway）
# ==========================
def get_db_connection():
    return pymysql.connect(
        host="trolley.proxy.rlwy.net",
        user="root",
        password="zeYpXtlGmlakPbbEbJJZOnZwDxONIrjw",
        database="railway",
        port=47683,
        cursorclass=pymysql.cursors.DictCursor
    )

# ==========================
# フィルター
# ==========================
def number_format(value):
    try:
        return "{:,}".format(int(value))
    except:
        return value

app.jinja_env.filters['number_format'] = number_format

# ==========================
# トップ
# ==========================
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("top.html", rooms=rooms)

@app.route("/top")
def top():
    return index()

# ==========================
# 会員登録
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        password_confirm = request.form.get("password_confirm").strip()
        email = request.form.get("email").strip()

        if not all([username, password, email]):
            flash("全て入力してください", "danger")
            return render_template("register.html")

        if password != password_confirm:
            flash("パスワードが一致しません", "danger")
            return render_template("register.html")

        hashed_pw = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (%s,%s,%s)",
                (username, hashed_pw, email)
            )
            conn.commit()
        except:
            flash("ユーザー名が既に使われています", "danger")
            return render_template("register.html")

        cursor.close()
        conn.close()

        flash("登録成功！ログインしてください", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ==========================
# ログイン
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            return redirect(url_for("top"))
        else:
            flash("ログイン失敗", "danger")

    return render_template("login.html")

# ==========================
# ログアウト
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ==========================
# 部屋詳細
# ==========================
@app.route("/detail/<int:room_id>")
def detail(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms WHERE id=%s", (room_id,))
    room = cursor.fetchone()

    cursor.close()
    conn.close()

    if not room:
        return "部屋が存在しません"

    return render_template("detail.html", room=room)

# ==========================
# 予約
# ==========================
@app.route("/reserve/<int:room_id>", methods=["GET", "POST"])
def reserve(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM rooms WHERE id=%s", (room_id,))
    room = cursor.fetchone()

    cursor.close()
    conn.close()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        checkin = request.form.get("checkin")
        checkout = request.form.get("checkout")
        people = request.form.get("people")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO reservations
            (user_id, room_id, name, email, checkin, checkout, people)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            session.get("user_id"),
            room_id,
            name,
            email,
            checkin,
            checkout,
            people
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("top"))

    return render_template("reserve.html", room=room)

# ==========================
# マイページ
# ==========================
@app.route("/my_reservations")
def my_reservations():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.*, rm.name AS room_name
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        WHERE r.user_id=%s
    """, (session["user_id"],))

    reservations = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("my_reservations.html", reservations=reservations)

# ==========================
# 実行
# ==========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)