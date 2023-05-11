from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from .bot_settings import cbq, constants, emoji


def get_args_back(
    text: str = "Назад",
    callback_query: str = cbq.GO_BACK,
    sign: str = emoji.GO_BACK,
) -> tuple[str, str]:
    return sign + text, callback_query


# BUTTONS ====================================================================
def __button(text: str, callback_data: str) -> InlineKeyboardButton:
    # callback_data has a size limitation of 64 bytes
    while len(callback_data.encode()) > 64:
        callback_data = callback_data[:-1]
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def get_button(text: str, callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup.from_button(__button(text, callback_data))


def add_footer(
    keyboard: list,
    footer: list[tuple[str, str]],
) -> list:
    keyboard.append([__button(item[0], item[1]) for item in footer])


def get_keyboard(
    args: list[tuple[str, str]] = None,
    *,
    header: list[tuple[str, str]] = None,
    footer: list[tuple[str, str]] = None,
    markup: bool = True,
    keyboard: list = None
) -> InlineKeyboardMarkup | list | None:
    if keyboard is not None:
        return InlineKeyboardMarkup(keyboard)
    keyboard = []
    if header is not None:
        keyboard.append([__button(item[0], item[1]) for item in header])
    if args is not None:
        if args == []:
            return None
        keyboard.extend([[__button(item[0], item[1])] for item in args])
    if footer is not None:
        add_footer(keyboard, footer)
    if markup:
        return InlineKeyboardMarkup(keyboard)
    return keyboard


# Backwards ==================================================================
def __add_if_unique(cache: list, data: str) -> None:
    if data not in cache:
        cache.append(data)


def add_backwards(
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    keyboard: InlineKeyboardMarkup = None,
) -> None:
    context.user_data[constants.CACHE] = context.user_data.get(constants.CACHE, [])
    __add_if_unique(context.user_data[constants.CACHE], (text, keyboard))


# === BOT Actions ============================================================
async def bot_send_data(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    keyboard: InlineKeyboardMarkup = None,
    *,
    backwards: bool = True,
    in_place: bool = True,
) -> None:
    if backwards:
        add_backwards(context, text, keyboard)
    if not in_place:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text.format(update.effective_user.first_name),
            reply_markup=keyboard,
        )
    elif update.message is not None:
        await update.message.reply_html(
            text.format(update.message.from_user.first_name),
            reply_markup=keyboard,
        )
    elif update.callback_query is not None:
        await update.callback_query.edit_message_text(
            text.format(update.callback_query.from_user.first_name),
            reply_markup=keyboard,
        )


# PARSING ====================================================================
def parse_data(data: Update | str, prefix: str) -> str:
    if isinstance(data, Update):
        data = data.callback_query.data
    return data.replace(prefix, "")


def reset_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    match step:
        case constants.LOCATION:
            temp = context.user_data[constants.AGE]
            context.user_data.clear()
            context.user_data[constants.COUNTRY] = "Россия"
            context.user_data[constants.AGE] = temp
        case constants.REGION:
            context.user_data.pop(constants.REGION, '')
        case constants.CITY_OR_AND_FUND:
            context.user_data.pop(constants.CITY, '')
            context.user_data.pop(constants.FUND, '')
            context.user_data[constants.REGION] = parse_data(update, cbq.GET_CITY_OR_AND_FUND)
        case constants.FUND:
            context.user_data.pop(constants.FUND, '')
            context.user_data[constants.CITY] = parse_data(update, cbq.GET_FUND)
            if context.user_data[constants.CITY] in constants.TWO_CAPITALS:
                context.user_data.pop(constants.REGION, '')


'''
async def remove_keyboard(update: Update, text: str = "") -> str:
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


# Callback_data checkers =====================================================
def is_city_requested(callback_data: str) -> bool:
    return callback_data.startswith(cbq.GET_CITY)


def is_fund_requested(callback_data: str) -> bool:
    return callback_data.startswith(cbq.GET_FUND)
'''
