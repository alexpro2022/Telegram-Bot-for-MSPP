from telegram import InlineKeyboardMarkup

from .bot_settings import button_text, cbq, constants, conversation
# from .models import CoverageArea, Fund
from .utils import get_args_back, get_button, get_keyboard


# NAVIGATION CONTROLS - управление навигацией =========================
def get_info(text: str, callback_data: str) -> tuple[str, InlineKeyboardMarkup]:
    return text, get_button(button_text.OK, callback_data)


def get_location() -> tuple[str, InlineKeyboardMarkup]:
    text = conversation.WHAT_LOCATION
    buttons = [
        (button_text.MSK, cbq.GET_FUND + constants.MSK),
        (button_text.MSK_reg, cbq.GET_FUND + constants.MSK_reg),
        (button_text.SPB, cbq.GET_FUND + constants.SPB),
        (button_text.OTHER_REGION, cbq.GET_REGION),
        (button_text.OUTSIDE_COUNTRY, cbq.GET_COUNTRY),
    ]
    footer = [get_args_back("Изменить возраст")]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


def get_country() -> tuple[str, InlineKeyboardMarkup]:
    text = conversation.CHOOSE_COUNTRY
    buttons = [
        (button_text.KAZ, cbq.GET_FUND + constants.COUNTRY),
        (button_text.OTHER_COUNTRY, cbq.NO_FUND),
    ]
    footer = [get_args_back("В начало")]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_region(parent_country: str | None = None) -> tuple[str, InlineKeyboardMarkup]:
    from .models import CoverageArea
    text = conversation.CHOOSE_REGION
    buttons = [
        (region.name, cbq.GET_CITY + region.name)
        async for region in CoverageArea.objects.filter(level=1)
        if region.name not in constants.TWO_CAPITALS
    ]
    footer = [get_args_back("В начало"), (button_text.NO_MY_REGION, cbq.NO_FUND)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_city(parent_region: str) -> tuple[str, InlineKeyboardMarkup]:
    from .models import CoverageArea
    text = conversation.CHOOSE_CITY + parent_region
    buttons = [
        (city.name, cbq.GET_FUND + city.name)
        async for city in CoverageArea.objects.filter(parent__name=parent_region)
    ]
    footer = [get_args_back("Изменить регион"), (button_text.NO_MY_CITY, cbq.NO_FUND)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_fund(parent_city: str, age: str) -> tuple[str, InlineKeyboardMarkup]:
    from .models import Fund
    text = conversation.CHOOSE_FUND + parent_city
    buttons = [
        (fund.name, cbq.GET_NEW_MENTOR_FORM + fund.name)
        async for fund in Fund.objects.filter(
            coverage_area__name=parent_city,
            age_limit__from_age__lte=int(age),
        )
    ]
    footer = [get_args_back("Изменить город"), (button_text.FUNDS_INFO, cbq.GET_FUNDS_INFO)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


def fund_missing() -> tuple[str, InlineKeyboardMarkup]:
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
        get_args_back("Изменить фонд", cbq.GET_FUND),
        (button_text.FINISH, cbq.SEND_SPREADSHEET),
    ]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard


'''
    buttons = [
        ("1 Арифметика добра", cbq.GET_APPLICATION_STARTED + "1 Арифметика добра"),
        ("2 Арифметика добра", cbq.GET_APPLICATION_STARTED + "2 Арифметика добра"),
        ("3 Арифметика добра", cbq.GET_APPLICATION_STARTED + "3 Арифметика добра"),
        ("4 Арифметика добра", cbq.GET_APPLICATION_STARTED + "4 Арифметика добра"),
        ("5 Арифметика добра", cbq.GET_APPLICATION_STARTED + "5 Арифметика добра"),
    ]'''
