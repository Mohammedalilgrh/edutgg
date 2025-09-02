@bot.message_handler(commands=['class'])
def class_start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🎓 Start Live Class", 
            url="https://your-enhanced-whiteboard.onrender.com"
        )
    )
    bot.send_message(
        message.chat.id,
        "🎯 Live Class Starting!\n\n"
        "📋 Subject: Mathematics - Trigonometry\n"
        "⏰ Time: 16:00\n"
        "👨‍🏫 Click below to join the interactive whiteboard:",
        reply_markup=markup
    )
