import os
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

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN"
        )

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("schedule", schedule))

    app.run_polling()

if __name__ == "__main__":
    main()
