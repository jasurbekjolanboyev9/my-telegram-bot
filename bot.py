import os
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from dotenv import load_dotenv

# Maxfiy ma'lumotlarni yuklash
load_dotenv()

# Bot tokenini oling
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Flask serveri
app = Flask(__name__)

# Boshlang'ich komandalar
def start(update, context):
    keyboard = [
        [InlineKeyboardButton("📂 Darsliklarni Yuklash", callback_data='upload')],
        [InlineKeyboardButton("📚 Qo'llanmalar", callback_data='manuals')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Salom! Kerakli bo'limni tanlang:", reply_markup=reply_markup)

# Tugma bosilganida javob berish
def button(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'upload':
        query.edit_message_text(text="📂 Video darsliklarni yuklash uchun fayl yuboring.")
    elif query.data == 'manuals':
        query.edit_message_text(text="📚 Qo'llanmalaringizni yuklash uchun fayl yuboring.")

# Fayl yuklash funksiyasi
def file_handler(update, context):
    file = update.message.document
    if file:
        if update.message.from_user.id == ADMIN_ID:  # Faqat admin fayl yuklay oladi
            file.download(file.file_name)
            update.message.reply_text("Fayl muvaffaqiyatli yuklandi.")
        else:
            update.message.reply_text("Sizda fayl yuklash uchun ruxsat yo'q.")
    else:
        update.message.reply_text("Iltimos, to'g'ri fayl yuboring.")

# Faqat admin uchun buyruq
def admin_command(update, context):
    if update.message.from_user.id == ADMIN_ID:
        update.message.reply_text("Siz admin sifatida tizimdasiz.")
    else:
        update.message.reply_text("Bu buyruq faqat adminlar uchun.")

# Telegram botni sozlash
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "OK", 200

# Flaskni ishlatish va webhookni sozlash
@app.route('/')
def index():
    return "Bot ishlamoqda!", 200

if __name__ == '__main__':
    # Updater va Dispatcher'ni sozlash
    updater = Updater(TOKEN, use_context=True)
    global bot
    bot = updater.bot
    global dp
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.document, file_handler))
    dp.add_handler(CommandHandler("admin", admin_command))

    # Heroku uchun webhook sozlash
    PORT = int(os.environ.get('PORT', 8443))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    bot.set_webhook("https://<HEROKU_APP_NAME>.herokuapp.com/" + TOKEN)

    app.run(host="0.0.0.0", port=PORT)
