import os
import threading
import requests

from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TWITCH_URL = "https://www.twitch.tv/aleksandr_merkyriev"
TELEGRAM_URL = "https://t.me/MerkyrievCRMP"
TIKTOK_URL = "https://www.tiktok.com/@twitch.merkyriev_"

CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "STREAM HUB is running!"

@web_app.route("/twitch-status")
def twitch_status():
    if not CLIENT_ID or not CLIENT_SECRET:
        return jsonify({"online": False, "error": "Twitch API not configured"})

    try:
        token_response = requests.post(
            "https://id.twitch.tv/oauth2/token",
            params={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "client_credentials"
            },
            timeout=10
        )
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        response = requests.get(
            "https://api.twitch.tv/helix/streams",
            headers={
                "Client-ID": CLIENT_ID,
                "Authorization": f"Bearer {access_token}"
            },
            params={"user_login": "aleksandr_merkyriev"},
            timeout=10
        )
        response.raise_for_status()
        streams = response.json().get("data", [])

        if streams:
            return jsonify({
                "online": True,
                "title": streams[0].get("title", ""),
                "viewers": streams[0].get("viewer_count", 0)
            })

        return jsonify({"online": False})

    except Exception:
        return jsonify({"online": False, "error": "Twitch check failed"}), 500

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Смотреть Twitch", url=TWITCH_URL)],
        [InlineKeyboardButton("Наш Telegram-канал", url=TELEGRAM_URL)],
        [InlineKeyboardButton("Мой TikTok", url=TIKTOK_URL)]
    ]

    await update.message.reply_text(
        "💜 Привет! Это официальный бот Merkyriev.\n\n"
        "📅 Стримы: понедельник–пятница в 18:00 по Москве.\n\n"
        "Нажми на кнопку ниже!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Расписание стримов:\n\n"
        "Понедельник–пятница — 18:00 по Москве.\n"
        "💜 Жду тебя на стриме!"
    )

def run_bot():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

    bot = Application.builder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("schedule", schedule))
    bot.run_polling(stop_signals=None)

def main():
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
