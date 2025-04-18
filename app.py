from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os, requests

app = Flask(__name__)
app.secret_key = 'nika_travel_secret'
DATA_FILE = 'data/tours.json'
UPLOAD_FOLDER = 'static/images'
ADMIN_PASSWORD = 'Kk12345#@'

TELEGRAM_TOKEN = '8198089868:AAFJndPCalVaUBhmKEUAv7qrUpkcOs52XEY'
TELEGRAM_CHAT_ID = '1894258213'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_tours():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tours(tours):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tours, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    tours = load_tours()
    return render_template('index.html', tours=tours)

@app.route('/tour/<int:tour_id>', methods=['GET', 'POST'])
def tour_detail(tour_id):
    tours = load_tours()
    tour = next((t for t in tours if t["id"] == tour_id), None)
    if not tour:
        return "Тур не найден", 404

    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        date = request.form.get('date')
        people = request.form.get('people')
        comment = request.form.get('comment')
        text = f"📩 Заявка на тур: {tour['title']}\n👤 Имя: {name}\n📱 Телефон: {phone}\n📅 Дата вылета: {date}\n👥 Кол-во человек: {people}\n💬 Комментарий: {comment or '—'}"
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", params={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        flash("Заявка отправлена!")
        return redirect(url_for('tour_detail', tour_id=tour_id))

    return render_template('tour.html', tour=tour)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        flash('Неверный пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template('admin.html', tours=load_tours())

@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        tours = load_tours()
        new_id = max((t["id"] for t in tours), default=0) + 1
        image_file = request.files.get('image_file')
        filename = image_file.filename if image_file else ''
        if filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
        new_tour = {
            "id": new_id,
            "title": request.form["title"],
            "price": int(request.form["price"]),
            "image": f"images/{filename}" if filename else "",
            "description": request.form["description"]
        }
        tours.append(new_tour)
        save_tours(tours)
        return redirect(url_for('admin'))
    return render_template('edit.html', action="Добавить", tour=None)

@app.route('/edit/<int:tour_id>', methods=['GET', 'POST'])
def edit(tour_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    tours = load_tours()
    tour = next((t for t in tours if t["id"] == tour_id), None)
    if not tour:
        return "Тур не найден", 404
    if request.method == 'POST':
        image_file = request.files.get('image_file')
        filename = image_file.filename if image_file else ''
        if filename:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            tour["image"] = f"images/{filename}"
        tour["title"] = request.form["title"]
        tour["price"] = int(request.form["price"])
        tour["description"] = request.form["description"]
        save_tours(tours)
        return redirect(url_for('admin'))
    return render_template('edit.html', action="Редактировать", tour=tour)

@app.route('/delete/<int:tour_id>')
def delete(tour_id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    tours = [t for t in load_tours() if t["id"] != tour_id]
    save_tours(tours)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
