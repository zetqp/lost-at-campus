from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# DB 초기화 함수
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            location TEXT,
            date TEXT,
            notes TEXT,
            contact TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 서버 시작 시 DB 초기화
init_db()

# 습득물 등록
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        item_name = request.form['item_name']
        location = request.form['location']
        date = request.form['date']
        notes = request.form['notes']
        contact = request.form['contact']

        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO items (item_name, location, date, notes, contact)
            VALUES (?, ?, ?, ?, ?)
        ''', (item_name, location, date, notes, contact))
        conn.commit()
        conn.close()

        return render_template('thankyou.html')
    return render_template('register.html')

# 분실물 검색
@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('''
            SELECT * FROM items
            WHERE item_name LIKE ? OR location LIKE ? OR notes LIKE ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        results = c.fetchall()
        conn.close()
    return render_template('search.html', results=results)

# 찾았어요 (삭제 기능)
@app.route('/found', methods=['GET', 'POST'])
def found():
    message = ''
    if request.method == 'POST':
        keyword = request.form['keyword']
        contact = request.form['contact']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute('''
            DELETE FROM items
            WHERE (item_name LIKE ? OR location LIKE ? OR notes LIKE ?)
            AND contact = ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', contact))
        conn.commit()
        if c.rowcount > 0:
            message = '등록된 정보가 삭제되었습니다.'
        else:
            message = '일치하는 정보가 없습니다.'
        conn.close()
    return render_template('found.html', message=message)

# 메인 페이지
@app.route('/')
def home():
    return render_template('home.html')

# 배포용
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
