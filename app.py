from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

DATA_FILE = 'data.csv'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        item_name = request.form['item_name']
        location = request.form['location']
        date = request.form['date']
        notes = request.form['notes']
        contact = request.form['contact']

        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([item_name, location, date, notes, contact])

        return render_template('thankyou.html')
    return render_template('register.html')

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').strip()
    results = []

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if keyword.lower() in ','.join(row).lower():
                    results.append(row)

    return render_template('search.html', results=results, keyword=keyword)

@app.route('/found', methods=['GET', 'POST'])
def found():
    message = ''
    if request.method == 'POST':
        keyword = request.form['keyword'].strip()
        contact = request.form['contact'].strip()

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                rows = list(csv.reader(f))
            new_rows = []
            found_match = False
            for row in rows:
                if keyword.lower() in ','.join(row).lower() and contact == row[-1]:
                    found_match = True
                else:
                    new_rows.append(row)

            if found_match:
                with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(new_rows)
                message = '찾아주셔서 감사합니다!'
            else:
                message = '일치하는 정보가 없습니다.'
    return render_template('found.html', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
