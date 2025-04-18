
import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
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

@app.route('/book/<int:tour_id>', methods=['POST'])
def book(tour_id):
    name = request.form['name']
    phone = request.form['phone']
    message = f"📩 Новая заявка\nИмя: {name}\nТелефон: {phone}\nТур ID: {tour_id}"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", params={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    })
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    tours = load_tours()
    return render_template('admin.html', tours=tours)

@app.route('/upload', methods=['POST'])
def upload():
    image = request.files['image']
    if image:
        filename = secure_filename(image.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(path)
    return redirect(url_for('admin'))

@app.route('/add', methods=['POST'])
def add():
    tours = load_tours()
    new_id = max(t['id'] for t in tours) + 1 if tours else 1
    tours.append({
        "id": new_id,
        "title": request.form['title'],
        "price": int(request.form['price']),
        "image": "images/" + request.form['image'],
        "description": request.form['description']
    })
    save_tours(tours)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run()
