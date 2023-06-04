import logging

from django.conf import settings
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from apps.bot.bot_settings import conversation
from apps.bot.utils import bot_send_data

logger = logging.getLogger(__name__)

GOOGLE_ENV_VARS = {
    "funds_spreadsheet_id": settings.FUNDS_SPREADSHEET_ID,
    "mentors_spreadsheet_id": settings.MENTORS_SPREADSHEET_ID,
    **settings.ENV_INFO,
}


def warning_no_google(msg: str, will: str = '') -> str:
    empty_vars = [f'{key}\n' for key, value
                  in GOOGLE_ENV_VARS.items()
                  if value is None or value == '_']
    if not empty_vars:
        return ''
    return conversation.WARNING_NO_GOOGLE.format(
        will=will,
        empty_env_vars=''.join(empty_vars), conclusion=msg)


def info_google(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        text = warning_no_google('Conversation terminated')
        if not text:
            await func(update, context)
            text = conversation.FORMS_FILLING_FINISH
        await bot_send_data(update, context, text)
        return ConversationHandler.END

    return wrapper
