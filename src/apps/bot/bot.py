from urllib.parse import urljoin

from telegram.error import TelegramError
from telegram.ext import Application

import config.settings as settings

from .handlers import HANDLERS
from .logger import logger

bot_app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
bot_app.add_handlers(HANDLERS)


async def start_bot():
    try:
        await bot_app.initialize()
        if settings.WEBHOOK_MODE:
            await bot_app.bot.set_webhook(urljoin(settings.WEBHOOK_URL, "bot/"))
        else:
            await bot_app.updater.start_polling()
        await bot_app.start()
    except (TelegramError, RuntimeError):
        logger.exception("Bot start sequence FAILED")
