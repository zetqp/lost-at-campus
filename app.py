import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploaded_photos'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 최대 16MB 업로드 제한
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# DB 초기화 함수
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 location TEXT,
                 date TEXT,
                 notes TEXT,
                 contact TEXT,
                 photo_filename TEXT)''')
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('INSERT INTO items (name, location, date, notes, contact, photo_filename) VALUES (?, ?, ?, ?, ?, ?)',
                  (name, location, date, notes, contact, photo_filename))
        conn.commit()
        conn.close()
        return render_template('thankyou.html')

    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    items = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        query = "SELECT * FROM items WHERE name LIKE ? OR location LIKE ? OR notes LIKE ?"
        like_keyword = f'%{keyword}%'
        c.execute(query, (like_keyword, like_keyword, like_keyword))
        items = c.fetchall()
        conn.close()
    return render_template('search.html', items=items)

@app.route('/found', methods=['GET', 'POST'])
def found():
    items = []
    message = ''
    if request.method == 'POST':
        keyword = request.form['keyword']
        contact = request.form['contact']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("DELETE FROM items WHERE (name LIKE ? OR location LIKE ? OR notes LIKE ?) AND contact = ?",
                  (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', contact))
        deleted = c.rowcount
        conn.commit()
        c.execute("SELECT * FROM items")
        items = c.fetchall()
        conn.close()
        if deleted > 0:
            message = f"{deleted}개의 항목이 삭제되었습니다."
        else:
            message = "조건에 맞는 항목이 없습니다."
    else:
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM items")
        items = c.fetchall()
        conn.close()

    return render_template('found.html', items=items, message=message)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    port = int(os.environ.get('PORT', 10000))  # Render가 지정하는 포트 사용
    app.run(host='0.0.0.0', port=port)
