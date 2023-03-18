from typing import List, Optional, Sequence, Tuple

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler

from . import bot_settings as s

cbq = s.CallbackQueries

__button = InlineKeyboardButton


def get_text(text: str) -> str:
    return text.format(s.USERNAME)


def button(text, callback_data, brackets=True):
    if brackets:
        return [__button(text, callback_data=callback_data)]
    return __button(text, callback_data=callback_data)


def __keyboard_gen(args):  # : Sequence):
    for item1, item2 in args:
        yield button(item1, item2) if isinstance(item1, str) \
            else [  # logic for two half-buttons in one line
                button(item1[0], item1[1], False),
                button(item2[0], item2[1], False)]


def get_keyboard(
    args: List, *,
    callback_data: bool = True,
    header: Optional[Tuple] = None,
    footer: Optional[Sequence] = None,
):
    buttons_args = args if callback_data else [(item, item) for item in args]
    if header is not None:
        buttons_args.insert(0, header)
    if footer is not None:
        if isinstance(footer[0], str):
            buttons_args.append(footer)
        else:
            buttons_args.extend(footer)
    return InlineKeyboardMarkup(tuple(__keyboard_gen(buttons_args)))


def markup_OK(callback_data):
    return InlineKeyboardMarkup([button(s.OK, callback_data)])


def is_requested(data: str, prefix: str):
    return True if data.startswith(prefix) else False


def is_city_requested(data: str) -> bool:
    return is_requested(data, cbq.GET_CITY)


def is_fund_requested(data: str) -> bool:
    return is_requested(data, cbq.GET_FUND) or data == cbq.GET_FUND


def is_backwards_requested(data: str) -> bool:
    return is_requested(data, cbq.GO_BACK)


def add_if_unique(stack: list, data: str):
    if data not in stack:
        stack.append(data)


def add_backwards(context, backwards: str):
    add_if_unique(context.user_data[cbq.STACK], backwards)


def check_region_for_exceptions(region):
    if region in s.TWO_CAPITALS:
        return "init"
    return "region"


def check_city_for_exceptions(city):
    if city in s.TWO_CAPITALS:
        return "init"
    if city == "country":
        return "country"
    return "city"


def initiate_user_data(context: ContextTypes.DEFAULT_TYPE):
    context.user_data[s.COUNTRY] = "Россия"
    context.user_data[cbq.STACK] = []


# === BOT Actions ======================================================
# to make bot_send_message
async def message(update: Update, text: str, reply=None):
    await update.message.reply_html(text, reply_markup=reply)


async def bot_say_by(update: Update, text: str) -> int:
    await message(update, text)
    return ConversationHandler.END


# to make as decorator later
async def bot_send_data(
    update: Update,
    text: str,
    keyboard: Optional[InlineKeyboardMarkup] = None,
) -> None:
    if update.message:
        await update.message.reply_html(text, reply_markup=keyboard)
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, reply_markup=keyboard)
