import os
import psycopg2
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploaded_photos'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL")

# DB 연결 함수
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# DB 초기화 함수
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT,
            date TEXT,
            notes TEXT,
            contact TEXT,
            photo_filename TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        date = request.form['date']
        notes = request.form['notes']
        contact = request.form['contact']
        photo = request.files.get('photo')

        photo_filename = None
        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO items (name, location, date, notes, contact, photo_filename)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (name, location, date, notes, contact, photo_filename))
        conn.commit()
        cur.close()
        conn.close()

        return render_template('thankyou.html')
    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    items = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM items
            WHERE name ILIKE %s OR location ILIKE %s OR notes ILIKE %s
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        items = cur.fetchall()
        cur.close()
        conn.close()
    return render_template('search.html', items=items)

@app.route('/found', methods=['GET', 'POST'])
def found():
    items = []
    message = ''
    if request.method == 'POST':
        keyword = request.form['keyword']
        contact = request.form['contact']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM items
            WHERE (name ILIKE %s OR location ILIKE %s OR notes ILIKE %s) AND contact = %s
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', contact))
        deleted = cur.rowcount
        conn.commit()

        cur.execute('SELECT * FROM items')
        items = cur.fetchall()
        cur.close()
        conn.close()

        message = f"{deleted}개의 항목이 삭제되었습니다." if deleted > 0 else "조건에 맞는 항목이 없습니다."
    else:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM items')
        items = cur.fetchall()
        cur.close()
        conn.close()

    return render_template('found.html', items=items, message=message)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=10000)
