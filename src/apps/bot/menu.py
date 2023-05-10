import logging

from telegram import InlineKeyboardMarkup

from .bot_settings import button_text, cbq, constants, conversation
# from .models import CoverageArea, Fund
from .utils import get_args_back, get_button, get_keyboard

logger = logging.getLogger(__name__)


def get_info(text: str, callback_data: str) -> tuple[str, InlineKeyboardMarkup]:
    return text, get_button(button_text.OK, callback_data)


def get_location() -> tuple[str, InlineKeyboardMarkup]:
    text = conversation.WHAT_LOCATION
    buttons = [
        (button_text.MSK, cbq.GET_FUND + constants.MSK),
        (button_text.MSK_REG, cbq.GET_FUND + constants.MSK_REG),
        (button_text.SPB, cbq.GET_FUND + constants.SPB),
        (button_text.OTHER_REGION, cbq.GET_REGION),
        (button_text.OUTSIDE_COUNTRY, cbq.GET_COUNTRY),
    ]
    keyboard = get_keyboard(buttons)
    return text, keyboard


def get_country() -> tuple[str, InlineKeyboardMarkup]:
    text = conversation.CHOOSE_COUNTRY
    buttons = [
        (button_text.KAZ, cbq.GET_FUND + constants.KAZ),
        (button_text.OTHER_COUNTRY, cbq.NO_FUND),
    ]
    footer = [get_args_back("В начало")]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_region(parent_country: str = "Россия") -> tuple[str, InlineKeyboardMarkup]:
    from .models import CoverageArea
    text = conversation.CHOOSE_REGION + parent_country
    buttons = [
        (region.name, cbq.GET_CITY_OR_AND_FUND + region.name)
        async for region in CoverageArea.objects.filter(level=1)
        if region.name not in constants.TWO_CAPITALS
    ]
    footer = [get_args_back("В начало"), (button_text.NO_MY_REGION, cbq.NO_FUND)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_city(parent_region: str, markup: bool = True) -> tuple[str, InlineKeyboardMarkup]:
    from .models import CoverageArea
    text = conversation.CHOOSE_CITY + parent_region
    buttons = [
        (city.name, cbq.GET_FUND + city.name)
        async for city in CoverageArea.objects.filter(parent__name=parent_region)
    ]
    footer = [get_args_back("Изменить регион"), (button_text.NO_MY_CITY, cbq.NO_FUND)]
    keyboard = get_keyboard(buttons, footer=footer, markup=markup)
    return text, keyboard


async def get_fund(parent_location: str, age: str, markup: bool = True) -> tuple[str, InlineKeyboardMarkup]:
    from .models import Fund
    text = conversation.CHOOSE_FUND + parent_location + f', возраст: {age}'
    funds = [fund async for fund in Fund.objects.filter(
        coverage_area__name=parent_location,
        age_limit__lte=int(age),
    )]
    buttons = [(fund.name, cbq.GET_NEW_MENTOR_FORM + fund.name) for fund in funds]
    if markup:
        footer = [get_args_back("Изменить город"), (button_text.FUNDS_INFO, cbq.GET_FUNDS_INFO)]
    else:
        footer = [(button_text.FUNDS_INFO, cbq.GET_FUNDS_INFO)]
    keyboard = get_keyboard(buttons, footer=footer, markup=markup)
    descriptions = [fund.description for fund in funds]
    return text, keyboard, descriptions


async def get_city_or_and_fund(parent_region: str, age: str) -> tuple[str, InlineKeyboardMarkup]:
    text_city, keyboard_city = await get_city(parent_region, markup=False)
    text_fund, keyboard_fund, descriptions = await get_fund(parent_region, age, markup=False)
    if keyboard_fund is not None and keyboard_city is not None:
        text = conversation.CHOOSE_FUND_OR_CITY + parent_region + f', возраст: {age}'
        keyboard = get_keyboard(keyboard=keyboard_fund + keyboard_city)
        return text, keyboard, descriptions
    if keyboard_city is not None:
        return text_city, get_keyboard(keyboard=keyboard_city)
    if keyboard_fund is not None:
        return text_fund, get_keyboard(keyboard=keyboard_fund), descriptions
    return None


def no_fund() -> tuple[str, InlineKeyboardMarkup]:
    text = conversation.NO_FUND_MESSAGE
    footer = [get_args_back(), (button_text.NEW_FUND, cbq.GET_NEW_FUND_FORM)]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard


def get_confirmation(data: dict) -> tuple[str, InlineKeyboardMarkup]:
    key_error_mesage = "Test data"
    text = conversation.BOT_SPEAKING + (
        f"Твои данные будут отправлены:\n\n"
        f"Фамилия:      {data.get('surname', key_error_mesage)}\n"
        f"Имя:          {data.get('name', key_error_mesage)}\n"
        f"Отчество:     {data.get('patronimic', key_error_mesage)}\n"
        f"Возраст:      {data.get('age', key_error_mesage)}\n"
        f"Регион:       {data.get('region', 'Нет региона')}\n"
        f"Город:        {data.get('city', 'Нет города')}\n"
        f"Локация:      {data.get('location', key_error_mesage)}\n"
        f"Профессия:    {data.get('occupation', key_error_mesage)}\n"
        f"E-mail:       {data.get('email', key_error_mesage)}\n"
        f"Телефон:      {data.get('phone_number', key_error_mesage)}\n"
        f"Фонд:         {data.get('fund', key_error_mesage)}\n\n"
    )
    footer = [
        get_args_back("Изменить фонд", cbq.GO_BACK),
        (button_text.FINISH, cbq.SEND_SPREADSHEET),
    ]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard
