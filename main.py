import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Kunci lokasi database JSON agar tidak tersesat di laptop
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_TASKS = os.path.join(BASE_DIR, "tasks.json")

def load_tasks():
    if not os.path.exists(FILE_TASKS):
        with open(FILE_TASKS, "w") as file:
            json.dump([], file, indent=4)
        return []
    try:
        with open(FILE_TASKS, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_tasks(tasks):
    with open(FILE_TASKS, "w") as file:
        json.dump(tasks, file, indent=4)

# Rute Utama Website Dashboard
@app.route('/')
def home():
    raw_tasks = load_tasks()
    hari_ini = datetime.now().date()
    processed_tasks = []

    # Olah data agar sisa hari bisa langsung tampil dengan warna menarik di web
    for task in raw_tasks:
        deadline_date = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        selisih = (deadline_date - hari_ini).days
        
        deadline_tampil = deadline_date.strftime("%d-%m-%Y")
        
        if selisih < 0:
            status_kelas = "terlambat"
            pesan_sisa = f"❌ Terlambat {abs(selisih)} hari!"
        elif selisih == 0:
            status_kelas = "terlambat"
            pesan_sisa = "🔥 DEADLINE HARI INI!"
        elif 1 <= selisih <= 3:
            status_kelas = "mepet"
            pesan_sisa = f"⏳ Sisa {selisih} hari lagi (Mepet!)"
        else:
            status_kelas = ""
            pesan_sisa = f"⏳ Sisa {selisih} hari lagi"

        processed_tasks.append({
            "nama": task["nama"],
            "deadline_tampil": deadline_tampil,
            "status_kelas": status_kelas,
            "pesan_sisa": pesan_sisa
        })

    return render_template('index.html', tasks=processed_tasks)

# Rute untuk menerima data inputan dari Form Web
@app.route('/tambah', methods=['POST'])
def tambah_tugas():
    nama = request.form.get('nama')
    deadline = request.form.get('deadline') # Dapat format YYYY-MM-DD dari browser
    
    if nama and deadline:
        tasks = load_tasks()
        tasks.append({"nama": nama, "deadline": deadline})
        save_tasks(tasks)
        
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Membaca PORT otomatis dari server Render, jika tidak ada pakai port 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
