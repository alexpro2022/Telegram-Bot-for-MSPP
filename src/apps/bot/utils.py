# import json

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ConversationHandler, ContextTypes

from . import bot_settings as s

cbq = s.CallbackQueries


# ARGS ====================================================================
def get_args_ahead(
    text: str = "Вперед",
    callback_query: str = "To be implemented",
    sign: str = " \U0001F449 ",
) -> tuple[str, str]:
    return text + sign, callback_query


def get_args_back(
    text: str = "Назад",
    callback_query: str = cbq.GO_BACK,
    sign: str = " \U0001F448 ",
) -> tuple[str, str]:
    return sign + text, callback_query
# ============================================================================================================================================


# MARKUPS ======================================================================================
def get_keyboard(
    args: list[tuple[str, str]] | None = None,
    *,
    header: list[tuple[str, str]] | None = None,
    footer: list[tuple[str, str]] | None = None,
) -> InlineKeyboardMarkup:
    keyboard = []
    if header is not None:
        keyboard.append(
            [InlineKeyboardButton(text=item[0], callback_data=item[1]) for item in header])
    if args is not None:
        keyboard.extend(
            [[InlineKeyboardButton(text=item[0], callback_data=item[1])] for item in args])
    if footer is not None:
        keyboard.append(
            [InlineKeyboardButton(text=item[0], callback_data=item[1]) for item in footer])
    return InlineKeyboardMarkup(keyboard)


def get_single_button(text: str, callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(text, callback_data=callback_data))


def get_markup_OK(callback_data: str) -> InlineKeyboardMarkup:
    return get_single_button(s.OK, callback_data)


async def remove_keyboard(update: Update, text: str = "") -> str:
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
# ============================================================================================================================================


def get_username(update: Update):
    return update.message.from_user.first_name


def set_username(update: Update):
    s.USERNAME = update.message.from_user.first_name


def get_text(text: str, insert: str | None = None) -> str:
    insert = s.USERNAME if insert is None else insert
    return text.format(insert)


# Callback_data handlers =====================================================================
def is_requested(data: str, prefix: str):
    return True if data.startswith(prefix) else False


def is_city_requested(callback_data: str) -> bool:
    return is_requested(callback_data, cbq.GET_CITY)


def is_fund_requested(callback_data: str) -> bool:
    return is_requested(callback_data, cbq.GET_FUND) or callback_data == cbq.GET_FUND


def is_backwards_requested(callback_data: str) -> bool:
    return is_requested(callback_data, cbq.GO_BACK)


# Bacwards ==================================================================================
def add_if_unique(stack: list, data: str) -> None:
    if data not in stack:
        stack.append(data)


def add_backwards(context: ContextTypes.DEFAULT_TYPE, backwards: str) -> None:
    add_if_unique(context.user_data[cbq.STACK], backwards)


def check_region_for_exceptions(region: str) -> str:
    if region in s.TWO_CAPITALS:
        return "init"
    return "region"


def check_city_for_exceptions(place: str) -> str:
    if place in s.TWO_CAPITALS:
        return "init"
    if place == "country":
        return "country"
    return "city"


# === BOT Actions ============================================================================================================================
async def message(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None
):
    await update.message.reply_html(text, reply_markup=keyboard)


async def bot_send_data(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    if update.message:
        await message(update, text, keyboard)
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, reply_markup=keyboard)


def set_text_by(context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    context.user_data[s.TEXT_SAY_BY] = text


async def bot_say_by(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = context.user_data.get(
        s.TEXT_SAY_BY,
        "You have to impement your text in the context.user_data['text_say_by']")
    await message(update, text)
    return ConversationHandler.END
