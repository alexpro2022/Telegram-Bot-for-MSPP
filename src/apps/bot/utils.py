from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from .bot_settings import cbq, constants, emoji


username = "To be implemented"


def get_args_back(
    text: str = "Назад",
    callback_query: str = cbq.GO_BACK,
    sign: str = emoji.GO_BACK,
) -> tuple[str, str]:
    return sign + text, callback_query


# BUTTONS ====================================================================
def __button(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def get_button(text: str, callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup.from_button(__button(text, callback_data))


def get_keyboard(
    args: list[tuple[str, str]] | None = None,
    *,
    header: list[tuple[str, str]] | None = None,
    footer: list[tuple[str, str]] | None = None,
) -> InlineKeyboardMarkup:
    keyboard = []
    if header is not None:
        keyboard.append([__button(item[0], item[1]) for item in header])
    if args is not None:
        keyboard.extend([[__button(item[0], item[1])] for item in args])
    if footer is not None:
        keyboard.append([__button(item[0], item[1]) for item in footer])
    return InlineKeyboardMarkup(keyboard)


async def remove_keyboard(update: Update, text: str = "") -> str:
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


# Callback_data handlers =====================================================
def __is_requested(data: str, prefix: str):
    return True if data.startswith(prefix) else False


def is_city_requested(callback_data: str) -> bool:
    return __is_requested(callback_data, cbq.GET_CITY)


def is_fund_requested(callback_data: str) -> bool:
    return __is_requested(callback_data, cbq.GET_FUND) or callback_data == cbq.GET_FUND


def is_backwards_requested(callback_data: str) -> bool:
    return __is_requested(callback_data, cbq.GO_BACK)


# Backwards ==================================================================
def add_if_unique(stack: list, data: str) -> None:
    if data not in stack:
        stack.append(data)


def add_backwards(context: ContextTypes.DEFAULT_TYPE, backwards: str) -> None:
    add_if_unique(context.user_data[cbq.STACK], backwards)


def check_region_for_exceptions(region: str) -> str:
    if region in constants.TWO_CAPITALS:
        return "init"
    return "region"


def check_city_for_exceptions(place: str) -> str:
    if place in constants.TWO_CAPITALS:
        return "init"
    if place == "country":
        return "country"
    return "city"


# === BOT Actions ============================================================
def get_username(update: Update | None = None) -> str:
    global username
    if update is not None:
        username = update.message.from_user.first_name
    return username


async def send_html(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None
) -> None:
    await update.message.reply_html(
        text.format(get_username(update)), reply_markup=keyboard)


async def bot_send_data(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    if update.message:
        return await send_html(update, text, keyboard)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        text.format(get_username()), reply_markup=keyboard)
