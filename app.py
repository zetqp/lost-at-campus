from flask import Flask, render_template, request

app = Flask(__name__)

found_items = []

@app.route('/', endpoint='home')  # <- 여기서 'home'이라는 엔드포인트 이름 부여
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        item = {
            'item_name': request.form.get('item_name', ''),
            'location': request.form.get('location', ''),
            'date': request.form.get('date', ''),
            'note': request.form.get('note', ''),
            'contact': request.form.get('contact', ''),
        }
        found_items.append(item)
        print("등록된 아이템 리스트:", found_items)
        return render_template('thankyou.html', item=item)
    return render_template('register.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        keyword = request.form.get('search_keyword', '').lower()
        results = [
            item for item in found_items
            if keyword in item['item_name'].lower() or keyword in item['location'].lower()
        ]
        print("검색 결과 개수:", len(results))
    return render_template('search.html', results=results)

@app.route('/found', methods=['GET', 'POST'])
def found():
    message = ''
    if request.method == 'POST':
        keyword = request.form.get('keyword', '').lower()
        contact = request.form.get('contact', '')
        initial_len = len(found_items)
        found_items[:] = [
            item for item in found_items
            if not (keyword in item['item_name'].lower() and item['contact'] == contact)
        ]
        if len(found_items) < initial_len:
            message = '정상적으로 삭제되었습니다.'
        else:
            message = '일치하는 정보가 없습니다.'
    return render_template('found.html', message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
