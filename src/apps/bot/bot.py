import logging

from django.conf import settings
from telegram.error import TelegramError
from telegram.ext import Application

from .handlers import HANDLERS

bot_app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
bot_app.add_handlers(HANDLERS)
logger = logging.getLogger(__name__)


async def start_bot():
    try:
        await bot_app.initialize()
        if settings.WEBHOOK_MODE:
            await bot_app.bot.set_webhook(settings.WEBHOOK_URL)
            logger.info("Application starting via WEBHOOK")
        else:
            await bot_app.updater.start_polling()
            logger.info("Application starting via POLLING")
        await bot_app.start()
    except (TelegramError, RuntimeError):
        logger.exception("Application start sequence FAILED")
