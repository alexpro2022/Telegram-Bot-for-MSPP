from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from .bot_settings import cbq, emoji


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


# Callback_data checkers =====================================================
def is_city_requested(callback_data: str) -> bool:
    return callback_data.startswith(cbq.GET_CITY)


def is_fund_requested(callback_data: str) -> bool:
    return callback_data.startswith(cbq.GET_FUND)


# Backwards ==================================================================
def add_if_unique(stack: list, data: str) -> None:
    if data not in stack:
        stack.append(data)


def add_backwards(context: ContextTypes.DEFAULT_TYPE, backwards: str) -> None:
    context.user_data[cbq.STACK] = context.user_data.get(cbq.STACK, [])
    add_if_unique(context.user_data[cbq.STACK], backwards)


# === BOT Actions ============================================================
async def bot_send_data(
    update: Update,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> Message | bool:
    if update.message is not None:
        await update.message.reply_html(
            text.format(update.message.from_user.first_name),
            reply_markup=keyboard,
        )
    elif update.callback_query is not None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text.format(update.callback_query.from_user.first_name),
            reply_markup=keyboard,
        )


# PARSING ====================================================================
def parse_data(data: Update | str, prefix: str) -> str:
    if isinstance(data, Update):
        data = data.callback_query.data
    return data.replace(prefix, "")
