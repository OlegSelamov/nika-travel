
import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "nika_secret"
app.config['UPLOAD_FOLDER'] = 'static/images'

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def load_tours():
    with open('data/tours.json', encoding='utf-8') as f:
        return json.load(f)

def save_tours(tours):
    with open('data/tours.json', 'w', encoding='utf-8') as f:
        json.dump(tours, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    tours = load_tours()
    return render_template('index.html', tours=tours)

@app.route('/tour/<int:tour_id>', methods=['GET', 'POST'])
def tour(tour_id):
    tours = load_tours()
    tour = next((t for t in tours if t["id"] == tour_id), None)
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        date = request.form['date']
        people = request.form['people']
        comment = request.form['comment']
        text = f"📩 Заявка\nТур: {tour['title']}\nИмя: {name}\nТелефон: {phone}\nДата: {date}\nКол-во человек: {people}\nКомментарий: {comment}"
        requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", params={"chat_id": TELEGRAM_CHAT_ID, "text": text})
        return redirect(url_for('index'))
    return render_template('tour.html', tour=tour)

@app.route('/admin')
def admin():
    if not session.get("admin"):
        return redirect("/login")
    tours = load_tours()
    return render_template('admin.html', tours=tours)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session.get("admin"):
        return redirect("/login")
    if request.method == 'POST':
        tours = load_tours()
        image = request.files['image']
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        tours.append({
            "id": max([t['id'] for t in tours]+[0]) + 1,
            "title": request.form['title'],
            "price": int(request.form['price']),
            "image": f"images/{filename}",
            "description": request.form['description']
        })
        save_tours(tours)
        return redirect('/admin')
    return render_template('edit.html', tour=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'Kk12345#@':
            session['admin'] = True
            return redirect('/admin')
    return render_template('login.html')

if __name__ == '__main__':
    app.run()
