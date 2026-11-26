import os
import threading

from flask import Flask
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TWITCH_URL = "https://www.twitch.tv/aleksandr_merkyriev"
TELEGRAM_URL = "https://t.me/MerkyrievCRMP"
TIKTOK_URL = "https://www.tiktok.com/@twitch.merkyriev_"

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "STREAM HUB is running!"


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    keyboard = [
        [
            InlineKeyboardButton(
                "Смотреть Twitch",
                url=TWITCH_URL
            )
        ],
        [
            InlineKeyboardButton(
                "Наш Telegram-канал",
                url=TELEGRAM_URL
            )
        ],
        [
            InlineKeyboardButton(
                "Мой TikTok",
                url=TIKTOK_URL
            )
        ],
    ]

    await update.message.reply_text(
        "💜 Привет! Это официальный бот Merkyriev.\n\n"
        "Здесь ты узнаешь о стримах и новостях.\n\n"
        "📅 Стримы: понедельник–пятница "
        "в 18:00 по Москве.\n\n"
        "Нажми на кнопку ниже!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def schedule(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "📅 Расписание стримов:\n\n"
        "Понедельник–пятница — 18:00 по Москве.\n"
        "💜 Жду тебя на стриме!"
    )


def run_bot():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN"
        )

    bot_app = Application.builder().token(token).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("schedule", schedule))

    bot_app.run_polling(stop_signals=None)


def main():
    threading.Thread(
        target=run_bot,
        daemon=True
    ).start()

    port = int(os.environ.get("PORT", "10000"))

    web_app.run(
        host="0.0.0.0",
        port=port
    )


if __name__ == "__main__":
    main()
