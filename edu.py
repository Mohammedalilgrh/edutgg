import telebot
import sqlite3
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # ← REPLACE WITH YOUR BOT TOKEN
ADMIN_ID = 123456789  # ← REPLACE WITH YOUR TELEGRAM ID
WHITEBOARD_URL = "https://your-whiteboard.onrender.com"  # ← WE'LL SET THIS LATER

bot = telebot.TeleBot(TOKEN)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        subscribed BOOLEAN DEFAULT FALSE,
        plan TEXT,
        start_date TEXT,
        total_paid REAL DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        schedule TEXT,
        price REAL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        user_id INTEGER,
        course_id INTEGER,
        date TEXT,
        status TEXT
    )''')
    conn.commit()
    conn.close()

# --- LOAD COURSES ---
def load_courses():
    if not os.path.exists("courses.json"):
        default = [
            {"title": "Mathematics - Trigonometry", "desc": "Learn sin, cos, tan", "schedule": "16:00 Daily", "price": 9.99},
            {"title": "Physics - Mechanics", "desc": "Newton's Laws & Motion", "schedule": "Mon/Wed/Fri 18:00", "price": 12.99}
        ]
        with open("courses.json", "w") as f:
            json.dump(default, f)
    with open("courses.json", "r") as f:
        return json.load(f)

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 My Courses", "📊 Stats", "🔗 Subscribe", "🔔 Reminders", "🎓 Join Class")
    bot.send_message(message.chat.id, f"👋 Hi {message.from_user.first_name}! Welcome to EduTeacherBot.", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📚 My Courses")
def show_courses(message):
    courses = load_courses()
    msg = "📘 Available Courses:\n\n"
    for i, c in enumerate(courses, 1):
        msg += f"{i}. {c['title']} ({c['schedule']})\n   💬 {c['desc']}\n   💰 ${c['price']} / month\n\n"
    bot.send_message(message.chat.id, msg)

@bot.message_handler(func=lambda m: m.text == "🔗 Subscribe")
def subscribe(message):
    bot.send_message(
        message.chat.id,
        "Choose a subscription plan:\n\n🟢 Monthly: $9.99\n🟡 3-Month: $25.00\n🟣 Lifetime: $49.99\n\n👉 Click here to pay: https://your-stripe-link.com",
        reply_markup=telebot.types.InlineKeyboardMarkup().add(
            telebot.types.InlineKeyboardButton("💳 Pay Now", url="https://buy.stripe.com/test_abc123")
        )
    )

@bot.message_handler(func=lambda m: m.text == "📊 Stats")
def stats(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ Access denied.")
        return
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE subscribed = 1")
    subs = c.fetchone()[0]
    c.execute("SELECT SUM(total_paid) FROM users")
    revenue = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    conn.close()
    bot.send_message(message.chat.id, f"""
📊 Admin Dashboard:
👤 Total Students: {total_users}
👥 Active Subscribers: {subs}
💰 Total Revenue: ${revenue:.2f}
""")

@bot.message_handler(func=lambda m: m.text == "🔔 Reminders")
def reminders(message):
    bot.send_message(message.chat.id, "⏰ Today's reminder: Math class at 16:00!")

@bot.message_handler(func=lambda m: m.text == "🎓 Join Class")
def join_class(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎓 Open Whiteboard", 
            url=WHITEBOARD_URL
        )
    )
    bot.send_message(
        message.chat.id,
        "🎯 Live Class Starting Now!\n\n"
        "📋 Subject: Mathematics - Trigonometry\n"
        "⏰ Time: 16:00\n"
        "👨‍🏫 Click below to join the interactive whiteboard:",
        reply_markup=markup
    )

# --- RUN BOT ---
if __name__ == "__main__":
    init_db()
    print("🚀 EduTeacherBot started!")
    bot.polling(none_stop=True)
