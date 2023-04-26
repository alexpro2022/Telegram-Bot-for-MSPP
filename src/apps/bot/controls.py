from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from . import bot_settings as s
# from .models import CoverageArea, Fund
from .utils import (
    get_args_back,
    get_keyboard,
    get_markup_OK,
    get_text,
)


cbq = s.CallbackQueries


# NAVIGATION CONTROLS - Органы управления навигацией ======================================================================
def get_info(text: str, callback_data):
    text = get_text(text)
    keyboard = get_markup_OK(callback_data)
    return text, keyboard


def get_init() -> tuple[str, InlineKeyboardMarkup]:
    text = get_text(s.WHAT_LOCATION)
    buttons = [
        (s.MSK + s.MOSCOW_EMOJI, cbq.GET_FUND + s.MSK),
        (s.SPB + s.SPB_EMOJI, cbq.GET_FUND + s.SPB),
        (s.MSK_reg + s.MSK_reg_EMOJI, cbq.GET_CITY + s.MSK_reg),
        (cbq.BUTTON_OTHER_REGION),
        (cbq.BUTTON_OTHER_COUNTRY),
    ]
    footer = [get_args_back("Изменить возраст")]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


def get_country() -> tuple[str, InlineKeyboardMarkup]:
    text = get_text(s.CHOOSE_COUNTRY)
    buttons = [
        (s.KAZAHSTAN + s.KAZAHSTAN_EMOJI, cbq.GET_FUND + s.COUNTRY),
        (cbq.OTHER_COUNTRY, cbq.NO_FUND + s.COUNTRY),
    ]
    footer = [get_args_back("В начало")]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_region(parent_country: str | None = None):
    from .models import CoverageArea
    text = get_text(s.CHOOSE_REGION)
    buttons = [
        (region.name, cbq.GET_CITY + region.name)
        async for region in CoverageArea.objects.filter(level=1)
        if region.name not in s.TWO_CAPITALS
    ]
    footer = [get_args_back("В начало"), (cbq.NO_MY_REGION_TEXT, cbq.NO_FUND + s.REGION)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_city(parent_region: str):
    from .models import CoverageArea
    text = get_text(s.CHOOSE_CITY, parent_region)
    buttons = [
        (city.name, cbq.GET_FUND + city.name)
        async for city in CoverageArea.objects.filter(parent__name=parent_region)
    ]
    footer = [get_args_back(), (cbq.NO_MY_CITY_TEXT, cbq.NO_FUND + s.CITY)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_fund(parent_city: str, age: int):
    from .models import Fund
    text = get_text(s.CHOOSE_FUND, parent_city)
    buttons = [
        (fund.name, cbq.GET_APPLICATION_STARTED + fund.name)
        async for fund in Fund.objects.filter(
            coverage_area__name=parent_city,
            age_limit__from_age__lte=age,
        )
    ]
    footer = [get_args_back("Изменить город"), (cbq.FUNDS_INFO_TEXT, cbq.GET_FUNDS_INFO)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


def get_fund_missing():
    text = get_text(s.NO_FUND_MESSAGE)
    footer = [get_args_back(), (s.NEW_FUND_CONFIRM_MESSAGE, cbq.GET_NEW_FUND_FORM)]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard


def get_application_started():
    text = get_text(s.APPLICATION_FORM_TEXT)
    footer = [get_args_back("Изменить фонд"), (s.TEXT_NEW_APPLICATION, cbq.NEW_APPLICATION_FORM)]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard


def get_confirmation(data: dict):
    KEY_ERROR_MESSAGE = "Test data"
    text = s.BOT_SPEAKING + (
        f"Твои данные будут отправлены:\n\n"
        f"Фамилия:      {data.get('surname', KEY_ERROR_MESSAGE)}\n"
        f"Имя:          {data.get('name', KEY_ERROR_MESSAGE)}\n"
        f"Отчество:     {data.get('patronimic', KEY_ERROR_MESSAGE)}\n"
        f"Возраст:      {data.get('age', KEY_ERROR_MESSAGE)}\n"
        f"Регион:       {data.get('region', 'Нет региона')}\n"
        f"Город:        {data.get('city', 'Нет города')}\n"
        f"Локация:      {data.get('location', KEY_ERROR_MESSAGE)}\n"
        f"Профессия:    {data.get('occupation', KEY_ERROR_MESSAGE)}\n"
        f"E-mail:       {data.get('email', KEY_ERROR_MESSAGE)}\n"
        f"Телефон:      {data.get('phone_number', KEY_ERROR_MESSAGE)}\n"
        f"Фонд:         {data.get('fund', KEY_ERROR_MESSAGE)}\n\n"
    )
    footer = [
        get_args_back("Изменить фонд", cbq.GET_FUND),
        # (s.EXIT_EMOJI + "Выход?", cbq.SAY_BY),
        (s.TEXT_FINISH, cbq.SEND_SPREADSHEET),
    ]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard


# PARSING ================================================================================================
def parse_data(data: str, prefix: str) -> str:
    if isinstance(data, Update):
        data = data.callback_query.data
    return data.replace(prefix, "")


def set_location(
    data: Update | str,
    prefix: str,
    location_name: str,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    context.user_data[location_name] = parse_data(data, prefix)
    return context.user_data[location_name]


'''
    buttons = [
        ("1 Арифметика добра", cbq.GET_APPLICATION_STARTED + "1 Арифметика добра"),
        ("2 Арифметика добра", cbq.GET_APPLICATION_STARTED + "2 Арифметика добра"),
        ("3 Арифметика добра", cbq.GET_APPLICATION_STARTED + "3 Арифметика добра"),
        ("4 Арифметика добра", cbq.GET_APPLICATION_STARTED + "4 Арифметика добра"),
        ("5 Арифметика добра", cbq.GET_APPLICATION_STARTED + "5 Арифметика добра"),
    ]'''
