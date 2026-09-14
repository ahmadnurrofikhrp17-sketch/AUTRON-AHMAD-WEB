import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import telebot

# =======================================================
# KUNCI RAHASIA UTAMA AUTRON
# =======================================================
TELEGRAM_TOKEN = "8905135611:AAGVpCyDx9d61MmESSGkZvel4omvuK-s7EY"
GMAIL_USER = "ahmadnurrofikhrp17@gmail.com"  # <--- Alamat Gmail kamu
GMAIL_PASSWORD = "gzrtomrqzlwczkwc"  # <--- Isi dengan 16 huruf dari Google tanpa spasi

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Kunci lokasi database JSON agar sinkron dengan web app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_TASKS = os.path.join(BASE_DIR, "tasks.json")

# =======================================================
# FUNGSI UNTUK MENGIRIM EMAIL OTOMATIS (SMTP SYSTEM)
# =======================================================
def kirim_email_reminder(nama_tugas, deadline_tugas):
    try:
        # 1. Konfigurasi Konten Surat Email
        pesan = MIMEMultipart()
        pesan['From'] = f"AUTRON Assistant <{GMAIL_USER}>"
        pesan['To'] = GMAIL_USER
        pesan['Subject'] = f"🚨 LOG TUGAS BARU TERCATAT: {nama_tugas}"

        # Isi surat berformat teks rapi
        isi_surat = (
            f"Halo Bos Ahmad,\n\n"
            f"Autron baru saja mencatat tugas/hafalan kuliah baru dari perintah Telegram Anda.\n\n"
            f"📌 NAMA TUGAS : {nama_tugas}\n"
            f"📅 DEADLINE   : {deadline_tugas}\n\n"
            f"Harap segera diselesaikan tepat waktu agar tidak menumpuk dan visi misi perusahaan kendaraan listrik Anda tetap fokus berjalan!\n\n"
            f"Salam,\n"
            f"AUTRON System v0.7"
        )
        pesan.attach(MIMEText(isi_surat, 'plain'))

        # 2. Proses Koneksi Aman ke Server Google Mail (SMTP)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Mengunci koneksi secara aman encryption
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        
        # Kirim suratnya!
        server.sendmail(GMAIL_USER, GMAIL_USER, pesan.as_string())
        server.quit()
        print("💡 [DEBUG] Surat email pemberitahuan sukses dikirim ke Gmail!")
        return True
    except Exception as e:
        print(f"❌ [DEBUG] Gagal mengirim email karena: {e}")
        return False

# =======================================================
# DATABASE MANAGER
# =======================================================
def load_tasks():
    if not os.path.exists(FILE_TASKS):
        return []
    try:
        with open(FILE_TASKS, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_tasks(tasks):
    with open(FILE_TASKS, "w") as file:
        json.dump(tasks, file, indent=4)

# =======================================================
# TELEGRAM HANDLER COMMANDS
# =======================================================
@bot.message_handler(commands=['start', 'help', 'bantuan'])
def kirim_sambutan(message):
    teks_sambut = (
        "⚡ HALO BOS AHMAD! AUTRON v0.7 EMAIL SYSTEM AKTIF ⚡\n\n"
        "Gunakan perintah ini untuk mengontrol saya:\n"
        "▶️ /cek - Untuk melihat daftar semua tugas & hafalan\n"
        "▶️ /tambah [nama] @ [DD-MM-YYYY] - Input tugas + Kirim Email Otomatis\n\n"
        "💡 *Contoh:* `/tambah Tugas Budaya Melayu @ 22-09-2026`"
    )
    bot.reply_to(message, teks_sambut, parse_mode="Markdown")

@bot.message_handler(commands=['tambah'])
def tambah_tugas_tele(message):
    isi_pesan = message.text.replace("/tambah ", "").strip()
    
    if "@" not in isi_pesan:
        bot.reply_to(message, "❌ *Format Salah, Bos!*\n\nGunakan: `/tambah Nama Tugas @ DD-MM-YYYY`", parse_mode="Markdown")
        return

    try:
        nama_tugas, tanggal_input = isi_pesan.split("@")
        nama_tugas = nama_tugas.strip()
        tanggal_input = tanggal_input.strip()

        deadline_date = datetime.strptime(tanggal_input, "%d-%m-%Y")
        
        tasks = load_tasks()
        tasks.append({
            "nama": nama_tugas,
            "deadline": deadline_date.strftime("%Y-%m-%d")
        })
        save_tasks(tasks)

        # 🚀 EKSEKUSI FITUR v0.7: Kirim email ke Gmail kamu secara otomatis!
        email_terkirim = kirim_email_reminder(nama_tugas, tanggal_input)
        
        notif_email = "📧 *Email pengingat dikirim ke Gmail!*" if email_terkirim else "⚠️ _Email gagal terkirim (Cek koneksi/sandi)._"

        bot.reply_to(message, f"✅ *Sukses Tercatat, Bos!*\n\n📌 Tugas: {nama_tugas}\n📅 Deadline: {tanggal_input}\n\n{notif_email}", parse_mode="Markdown")

    except ValueError:
        bot.reply_to(message, "❌ *Tanggal Rusak!* Gunakan format: *DD-MM-YYYY*", parse_mode="Markdown")

@bot.message_handler(commands=['cek'])
def cek_tugas(message):
    tasks = load_tasks()
    if len(tasks) == 0:
        bot.reply_to(message, "💡 Autron: Database bersih bos!", parse_mode="Markdown")
        return

    hari_ini = datetime.now().date()
    respon_chat = "📋 *DAFTAR TUGAS & HAFALAN KULIAH:*\n"
    for i, task in enumerate(tasks, start=1):
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d").date()
        sisa_hari = (deadline - hari_ini).days
        respon_chat += f"\n{i}. *{task['nama']}*\n   📅 Deadline: {deadline.strftime('%d-%m-%Y')}\n   ⏳ Sisa {sisa_hari} hari lagi\n"

    bot.reply_to(message, respon_chat, parse_mode="Markdown")

print("⚡ AUTRON v0.7 Upgrade Sukses! Email notification system stands by...")
bot.infinity_polling()
