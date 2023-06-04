import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from apps.google.utils import warning_no_google
from .bot_settings import button_text, cbq, constants, conversation, emoji

logger = logging.getLogger(__name__)


# Standard button's arguments
def get_args_back_button(
    text: str = button_text.BACK_BUTTON,
    callback_query: str = cbq.GO_BACK,
    sign: str = emoji.GO_BACK,
) -> tuple[str, str]:
    return sign + text, callback_query


def get_args_prev_menu_button(
    text: str = button_text.PREV_MENU_BUTTON,
    callback_query: str = cbq.GO_PREV_MENU,
    sign: str = emoji.PREV_MENU,
) -> tuple[str, str]:
    return sign + text, callback_query


def get_args_next_menu_button(
    text: str = button_text.NEXT_MENU_BUTTON,
    callback_query: str = cbq.GO_NEXT_MENU,
    sign: str = emoji.NEXT_MENU,
) -> tuple[str, str]:
    return text + sign, callback_query


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
    keyboard: list = None,
    markup: bool = True,
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
        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
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


def reset_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE, step: str) -> None:
    match step:
        case constants.LOCATION:
            temp = context.user_data[constants.AGE]
            context.user_data.clear()
            context.user_data[constants.COUNTRY] = "Россия"
            context.user_data[constants.AGE] = temp
            context.user_data[constants.REGION_CURRENT_PAGE] = 1
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


def get_values_for(what: str, data: dict) -> list | None:
    """Returns a list of values to be sent to Google spreadsheet.
       Param 'what' is expected to be either 'fund' or 'mentor'.
       Raises AssertionError otherwise.
    """
    assert what in ('fund', 'mentor'), 'Wrong parameter "what" = {what}'
    common_keys1 = ['surname', 'name']
    common_keys2 = ['email', 'phone_number', constants.AGE]
    mentor_keys = common_keys1 + ['patronimic', 'occupation'] + common_keys2 + [
        constants.REGION, constants.CITY] + [constants.FUND]
    fund_keys = common_keys1 + common_keys2 + ['location'] + [constants.FUND]

    match what:
        case 'fund':
            return [data.get(key) for key in fund_keys]
        case 'mentor':
            return [data.get(key) for key in mentor_keys]
    return None


def get_no_google_warning():
    return conversation.PRESS_BUTTON_TO_FILL_FORM + warning_no_google(
        conversation.CONTINUE_FILLING_FORM, will='будут')
