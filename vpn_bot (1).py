import sqlite3
import time
import logging
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Отключаем ВСЕ логи TeleBot
logging.getLogger('telebot').setLevel(logging.CRITICAL)
logging.getLogger('aiohttp').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

TOKEN = "8340813193:AAGakClybhKs8alnCzErHjU84CxKpo_HnSs"  # ← ВСТАВЬ ТОКЕН!
VPN_LINK = "https://cutt.ly/morhinevpn"

bot = TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        agreed BOOLEAN DEFAULT FALSE
    )''')
    conn.commit()
    conn.close()

def has_agreed(user_id):
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute("SELECT agreed FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0]

def set_agreed(user_id):
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, agreed) VALUES (?, TRUE)", (user_id,))
    conn.commit()
    conn.close()

def rules_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("✅ СОГЛАСЕН", callback_data="agree"))
    return keyboard

def link_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("🔗 Получить VPN", url=VPN_LINK))
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    init_db()
    
    if has_agreed(user_id):
        bot.send_message(message.chat.id, "🔗 Вот ссылка на VPN:", reply_markup=link_keyboard(), parse_mode='Markdown', disable_web_page_preview=True)
    else:
        rules_text = """🔒 ПРАВИЛА VPN

⚠️ VPN из сторонних платформ. НЕ несем ответственность за анонимность.

✅ Обход белых списков — ТОЛЬКО при необходимости.

🚫 НЕ использовать при серфинге на:
• Ozon
• Wildberries
• Яндекс сервисы
• Max
• Госуслуги
• Mail.ru
• ВКонтакте

Чтобы обходы не блокировало!

Прочитал? Жми "СОГЛАСЕН" """
        bot.send_message(message.chat.id, rules_text, reply_markup=rules_keyboard(), parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "agree")
def agree_callback(call):
    user_id = call.from_user.id
    set_agreed(user_id)
    bot.edit_message_text("✅ Согласен! Вот ссылка на VPN:", call.message.chat.id, call.message.message_id, reply_markup=link_keyboard(), parse_mode='Markdown')
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    print("🚀 Бот запускается...")
    init_db()
    
    while True:
        try:
            print("✅ Polling активен...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except KeyboardInterrupt:
            print("🛑 Остановка по Ctrl+C")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 5 сек...")
            time.sleep(5)
