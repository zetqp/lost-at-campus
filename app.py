import os
import psycopg2
from psycopg2 import pool, extras
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ───────────────────────────────
# 1) 환경변수 로드 (.env 로컬 개발용)
# ───────────────────────────────
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL 환경변수가 설정되지 않았습니다.\n"
        "Render 대시보드 혹은 .env 파일에 PostgreSQL 연결 문자열을 넣어주세요."
    )

# ───────────────────────────────
# 2) Flask 앱 설정
# ───────────────────────────────
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploaded_photos"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXT = {"png", "jpg", "jpeg", "gif"}

# ───────────────────────────────
# 3) PostgreSQL 연결 풀
# ───────────────────────────────
conn_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL,
    cursor_factory=extras.RealDictCursor,
)

def get_conn():
    return conn_pool.getconn()

def put_conn(c):
    conn_pool.putconn(c)

# ───────────────────────────────
# 4) DB 초기화 (한 번만)
# ───────────────────────────────
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
          id SERIAL PRIMARY KEY,
          name TEXT NOT NULL,
          location TEXT,
          date TEXT,
          notes TEXT,
          contact TEXT,
          photo_filename TEXT
        )
        """
    )
    conn.commit()
    put_conn(conn)

# ───────────────────────────────
# 5) 헬퍼
# ───────────────────────────────
def allowed(fname):
    return "." in fname and fname.rsplit(".", 1)[1].lower() in ALLOWED_EXT

# ───────────────────────────────
# 6) ROUTES
# ───────────────────────────────
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.files.get("photo")
        filename = None
        if f and allowed(f.filename):
            filename = secure_filename(f.filename)
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        values = (
            request.form["name"],
            request.form["location"],
            request.form["date"],
            request.form["notes"],
            request.form["contact"],
            filename,
        )
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO items
               (name, location, date, notes, contact, photo_filename)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            values,
        )
        conn.commit()
        put_conn(conn)
        return render_template("thankyou.html")

    return render_template("register.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    items = []
    if request.method == "POST":
        kw = request.form["keyword"]
        like = f"%{kw}%"
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT * FROM items
               WHERE name ILIKE %s OR location ILIKE %s OR notes ILIKE %s
               ORDER BY id DESC""",
            (like, like, like),
        )
        items = cur.fetchall()
        put_conn(conn)
    return render_template("search.html", items=items)

@app.route("/found", methods=["GET", "POST"])
def found():
    message = ""
    conn = get_conn()
    cur = conn.cursor()
    if request.method == "POST":
        kw = request.form["keyword"]
        contact = request.form["contact"]
        like = f"%{kw}%"
        cur.execute(
            """DELETE FROM items
               WHERE (name ILIKE %s OR location ILIKE %s OR notes ILIKE %s)
                 AND contact = %s""",
            (like, like, like, contact),
        )
        deleted = cur.rowcount
        conn.commit()
        message = f"{deleted}개 삭제" if deleted else "조건에 맞는 항목이 없습니다."
    cur.execute("SELECT * FROM items ORDER BY id DESC")
    items = cur.fetchall()
    put_conn(conn)
    return render_template("found.html", items=items, message=message)

# ───────────────────────────────
if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

