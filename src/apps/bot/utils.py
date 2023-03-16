from typing import List, Optional, Sequence, Tuple

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from . import bot_settings as s

cbq = s.CallbackQueries

__button = InlineKeyboardButton


def get_text(text):
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


def is_back(data: str) -> bool:
    return is_requested(data, cbq.GO_BACK)


def add_if_unique(
        stack: list,
        text: str,
        keyboard: InlineKeyboardMarkup
) -> None:
    data = {"text": text, "keyboard": keyboard}
    if data not in stack:
        stack.append(data)
