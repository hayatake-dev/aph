from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'your_very_secret_key_999'
# ==========================
# Jinja2カスタムフィルター
# ==========================
def number_format(value):
    """数字をカンマ区切りにする"""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value
app.jinja_env.filters['number_format'] = number_format

# ==========================
# MySQL接続
# ==========================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db22_system"
    )

# ==========================
# トップページ
# ==========================
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()

    # トップ用：おすすめ飲食店（例：安くて人気）
    cursor.execute("""
        SELECT r.*
        FROM restaurants r
        WHERE r.price_max <= 1500
        ORDER BY r.id DESC
        LIMIT 6
    """)
    restaurants = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "top.html",
        rooms=rooms,
        restaurants=restaurants,
        checkin=request.args.get("checkin", ""),
        checkout=request.args.get("checkout", ""),
        people=request.args.get("people", "")
    )
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
        agree_terms = request.form.get("agree_terms")

        if not all([username, password, email, agree_terms]):
            flash("全ての項目と利用規約への同意が必要です。", "danger")
            return render_template("register.html")
        if password != password_confirm:
            flash("パスワードが一致しません。", "danger")
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
        except mysql.connector.IntegrityError:
            flash("そのユーザー名は既に使用されています。", "danger")
            cursor.close()
            conn.close()
            return render_template("register.html")
        cursor.close()
        conn.close()
        flash("会員登録完了！ログインしてください。", "success")
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
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]
            flash(f"ようこそ、{username}さん！", "success")
            return redirect(url_for("top"))
        else:
            flash("ユーザー名またはパスワードが正しくありません。", "danger")
    return render_template("login.html")

# ==========================
# ログアウト
# ==========================
@app.route("/logout")
def logout():
    session.clear()
    flash("ログアウトしました。", "info")
    return redirect(url_for("index"))

# ==========================
# 部屋詳細
# ==========================
@app.route("/detail/<int:room_id>")
def detail(room_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE id=%s", (room_id,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    if not room:
        return "部屋が見つかりません", 404
    return render_template("detail.html", room=room)

# ==========================
# 予約フォーム
# ==========================
@app.route("/reserve/<int:room_id>", methods=["GET", "POST"])
def reserve(room_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE id=%s", (room_id,))
    room = cursor.fetchone()
    cursor.execute("SELECT * FROM room_plans WHERE room_id=%s", (room_id,))
    plans = cursor.fetchall()
    cursor.close()
    conn.close()

    if not room:
        flash("部屋が存在しません。", "danger")
        return redirect(url_for("top"))

    if request.method == "POST":
        name = request.form.get("name") if "user_id" not in session else session["username"]
        email = request.form.get("email") if "user_id" not in session else session["email"]
        plan_id = request.form.get("plan_id", type=int)
        if not plan_id:
            flash("プランを選択してください。", "danger")
            return render_template("reserve.html", room=room, plans=plans)

        checkin = request.form.get("checkin")
        checkout = request.form.get("checkout")
        people = request.form.get("people", type=int)
        breakfast = 1 if request.form.get("breakfast") == "on" else 0

        if not all([checkin, checkout, people]):
            flash("必須項目が未入力です。", "danger")
            return render_template("reserve.html", room=room, plans=plans)

        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d").date()
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d").date()
            nights = (checkout_date - checkin_date).days
            if nights <= 0:
                raise ValueError
        except ValueError:
            flash("宿泊日が不正です。", "danger")
            return render_template("reserve.html", room=room, plans=plans)

        selected_plan = next((p for p in plans if p["id"] == plan_id), None)
        if not selected_plan:
            flash("選択されたプランが存在しません。", "danger")
            return render_template("reserve.html", room=room, plans=plans)

        # 料金計算
        total_price = room['price'] + selected_plan['price_modifier']
        if breakfast:
            total_price += 1000
        total_price *= nights * people

        session['reservation'] = {
            "room_id": room_id,
            "plan_id": plan_id,
            "name": name,
            "email": email,
            "checkin": checkin,
            "checkout": checkout,
            "people": people,
            "breakfast": breakfast,
            "total_price": total_price
        }

        return redirect(url_for("confirm"))

    return render_template("reserve.html", room=room, plans=plans)

# ==========================
# 予約確認
# ==========================
@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    reservation = session.get('reservation')
    if not reservation:
        flash("予約情報がありません。", "warning")
        return redirect(url_for("top"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms WHERE id=%s", (reservation['room_id'],))
    room = cursor.fetchone()
    cursor.execute("SELECT * FROM room_plans WHERE id=%s", (reservation['plan_id'],))
    plan = cursor.fetchone()
    cursor.close()
    conn.close()

    # 宿泊日数
    checkin_date = datetime.strptime(reservation['checkin'], "%Y-%m-%d").date()
    checkout_date = datetime.strptime(reservation['checkout'], "%Y-%m-%d").date()
    nights = (checkout_date - checkin_date).days
    if nights <= 0:
        flash("宿泊日が不正です。", "danger")
        return redirect(url_for("reserve", room_id=reservation['room_id']))

    if request.method == "POST":
        breakfast_int = 1 if reservation['breakfast'] == "on" or reservation['breakfast'] == 1 else 0
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO reservations 
        (user_id, room_id, plan_id, name, email, checkin, checkout, people, breakfast, total_price, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'confirmed')
    """, (
        session.get("user_id"),
        reservation['room_id'],
        reservation['plan_id'],
        reservation['name'],
        reservation['email'],
        reservation['checkin'],
        reservation['checkout'],
        reservation['people'],
        breakfast_int,  
        reservation['total_price']
    ))
        conn.commit()
        cursor.close()
        conn.close()
        session.pop('reservation', None)
        flash("予約が完了しました！", "success")
        return redirect(url_for("my_reservations"))

    return render_template(
        "confirm.html",
        room=room,
        plan=plan,
        reservation=reservation,
        nights=nights
    )

# ==========================
# マイページ
# ==========================
@app.route("/my_reservations")
def my_reservations():
    if 'user_id' not in session:
        flash("ログインが必要です。", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, rm.name AS room_name, rp.plan_name
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        JOIN room_plans rp ON r.plan_id = rp.id
        WHERE r.user_id=%s
        ORDER BY r.checkin DESC
    """, (session['user_id'],))
    reservations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("my_reservations.html", reservations=reservations)

# ==========================
# 空室検索
# ==========================
@app.route("/search")
def search_rooms():
    checkin_str = request.args.get("checkin")
    checkout_str = request.args.get("checkout")
    people = int(request.args.get("people", 1))
    room_type = request.args.get("room_type")

    if not checkin_str or not checkout_str:
        return redirect(url_for("index"))

    try:
        checkin = datetime.strptime(checkin_str, "%Y-%m-%d").date()
        checkout = datetime.strptime(checkout_str, "%Y-%m-%d").date()
    except ValueError:
        return redirect(url_for("index"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rooms")
    rooms = cursor.fetchall()
    cursor.execute("SELECT * FROM reservations")
    reservations = cursor.fetchall()
    cursor.close()
    conn.close()

    available_rooms = []
    fallback_rooms = []

    for room in rooms:
        if room["capacity"] < people:
            continue
        if room_type and room["type"] != room_type:
            continue

        is_available = True
        for r in reservations:
            if r["room_id"] != room["id"]:
                continue
            r_checkin = r["checkin"]
            r_checkout = r["checkout"]
            if not (checkout <= r_checkin or checkin >= r_checkout):
                is_available = False
                break

        if is_available:
            available_rooms.append(room)
        else:
            fallback_rooms.append(room)

    return render_template(
        "search_result.html",
        rooms=available_rooms,
        fallback_rooms=fallback_rooms,
        checkin=checkin_str,
        checkout=checkout_str,
        people=people
    )

# ==========================
# 実行
# ==========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
