# from typing import Optional, Union

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from . import bot_settings as s

cbq = s.CallbackQueries


def __add(
    data: tuple,
    context: ContextTypes.DEFAULT_TYPE,
):
    if hasattr(context.user_data, cbq.STACK):
        context.user_data[cbq.STACK].append(data)
    else:
        context.user_data[cbq.STACK] = [data]


def __add_if_unique(
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    # data = {"text": text, "keyboard": keyboard}
    data = (text, keyboard)
    if data not in context.user_data:  # means unique
        __add(data, context)


# === try send from func named tuples
def bot_sending_data(func):   # Union[str, InlineKeyboardMarkup, Optional[bool]]):
    # : === Union[str, InlineKeyboardMarkup, Optional[bool]]):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # === func returns text, keyboard and backward
        res = await func(update, context)
        match len(res):
            case 3:
                text, keyboard, backward = res
            case 2:
                text, keyboard, backward = [*res, True]
            case 1:
                text, keyboard, backward = res, None, False
        # === Some bullshit which i still don't understand
        if update.message:
            await update.message.reply_html(text, reply_markup=keyboard)
        else:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(
                text, reply_markup=keyboard)
        # === Storage into Telegram.user_data
        if backward:
            __add_if_unique(context, text, keyboard)
    return wrapper
