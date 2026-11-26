

import os
import time
import threading
import requests

from flask import Flask, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TWITCH_URL = "https://www.twitch.tv/aleksandr_merkyriev"
TELEGRAM_URL = "https://t.me/MerkyrievCRMP"
TIKTOK_URL = "https://www.tiktok.com/@twitch.merkyriev_"
TWITCH_LOGIN = "aleksandr_merkyriev"
TELEGRAM_CHANNEL = "@MerkyrievCRMP"

CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

web_app = Flask(__name__)


@web_app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = (
        "https://faraeasdas-alt.github.io"
    )
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


@web_app.route("/")
def home():
    return "STREAM HUB is running!"


def get_twitch_stream():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Twitch API не настроен")

    token_response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]

    response = requests.get(
        "https://api.twitch.tv/helix/streams",
        headers={
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {access_token}",
        },
        params={"user_login": TWITCH_LOGIN},
        timeout=10,
    )
    response.raise_for_status()

    streams = response.json().get("data", [])
    return streams[0] if streams else None


@web_app.route("/twitch-status")
def twitch_status():
    try:
        stream = get_twitch_stream()

        if stream:
            return jsonify({
                "online": True,
                "title": stream.get("title", ""),
                "viewers": stream.get("viewer_count", 0),
            })

        return jsonify({"online": False})

    except Exception as error:
        print("Twitch API error:", error)
        return jsonify({
            "online": False,
            "error": "Twitch check failed",
        }), 500


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Смотреть Twitch", url=TWITCH_URL)],
        [InlineKeyboardButton("Наш Telegram-канал", url=TELEGRAM_URL)],
        [InlineKeyboardButton("Мой TikTok", url=TIKTOK_URL)],
    ]

    await update.message.reply_text(
        "💜 Привет! Это официальный бот Merkyriev.\n\n"
        "Здесь ты узнаешь о стримах и новостях.\n\n"
        "📅 Стримы: понедельник–пятница в 18:00 по Москве.\n\n"
        "Нажми на кнопку ниже!",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 Расписание стримов:\n\n"
        "Понедельник–пятница — 18:00 по Москве.\n"
        "💜 Жду тебя на стриме!"
    )


def send_stream_notification(stream):
    if not BOT_TOKEN:
        print("Не задан TELEGRAM_BOT_TOKEN")
        return

    title = stream.get("title") or "Прямой эфир"
    message = (
        "🔴 MERKYRIEV НАЧАЛ СТРИМ!\n\n"
        f"🎮 {title}\n\n"
        f"📺 Смотреть эфир: {TWITCH_URL}"
    )

    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHANNEL,
            "text": message,
        },
        timeout=15,
    )
    response.raise_for_status()
    print("Уведомление о начале стрима отправлено в Telegram")


def monitor_twitch():
    was_online = False

    while True:
        try:
            stream = get_twitch_stream()
            is_online = stream is not None

            if is_online and not was_online:
                send_stream_notification(stream)

            was_online = is_online

        except Exception as error:
            print("Ошибка проверки Twitch или отправки уведомления:", error)

        time.sleep(60)


def run_bot():
    if not BOT_TOKEN:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN")

    bot = Application.builder().token(BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("schedule", schedule))
    bot.run_polling(stop_signals=None)


def main():
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=monitor_twitch, daemon=True).start()

    port = int(os.environ.get("PORT", "10000"))
    web_app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
