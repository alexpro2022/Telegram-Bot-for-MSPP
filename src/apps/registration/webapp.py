import json
import logging

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import ContextTypes

from apps.bot.bot_settings import button_text, constants, conversation
from apps.bot.utils import add_backwards, bot_send_data
from apps.google.utils import warning_no_google

logger = logging.getLogger(__name__)


async def webapp(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str,
    message_text: str = conversation.PRESS_BUTTON_TO_FILL_FORM,
    button_text: str = button_text.FILL_FORM,
) -> None:
    keyboard = ReplyKeyboardMarkup.from_button(
        KeyboardButton(button_text, web_app=WebAppInfo(url=url)))
    await bot_send_data(
        update, context,
        message_text + warning_no_google(msg=conversation.CONTINUE_FILLING_FORM, will='будут'),
        keyboard, backwards=False, in_place=False)


async def read_web_app(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str | None:
    """
    Loads WebApp data,
    checks if WebApp BackButton has been clicked and returns back then or
    else populates context.user_data with loaded WebApp data.
    """
    data = json.loads(update.effective_message.web_app_data.data)
    if back := data.get("back") is not None:
        add_backwards(context, "fund", None)
        return back
    for key in data:
        if key == 'fund':
            context.user_data[constants.FUND] = data[key]
        else:
            context.user_data[key] = data[key]
    return None
