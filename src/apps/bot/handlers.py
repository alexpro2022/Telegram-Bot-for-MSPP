import json

from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config.settings import WEBAPP_HTML

# from src.apps.core.services.spreadsheets.runner import send_to_google_sheets
from . import bot_settings as s
from . import controls
from .utils import (
    add_backwards,
    bot_send_data,
    bot_say_by,
    check_city_for_exceptions,
    check_region_for_exceptions,
    # get_args_ahead,
    get_args_back,
    get_keyboard,
    get_text,
    is_backwards_requested,
    is_city_requested,
    is_fund_requested,
    # get_markup_OK,
    message,
    set_username,
)

from apps.core.services.spreadsheets.runner import send_to_google_sheets

cbq = s.CallbackQueries


def initiate_user_data(context: ContextTypes.DEFAULT_TYPE):
    age = context.user_data.get(s.AGE, 17)
    context.user_data.clear()
    context.user_data[s.COUNTRY] = "Россия"
    context.user_data[s.AGE] = age
    context.user_data[cbq.STACK] = []


# 1: GREETINGS ==================================================================================================================
async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_username(update)
    text, keyboard = controls.get_info(s.GREETING, cbq.GET_AGE)
    await message(update, text, keyboard)
    return s.MAIN_CONVERSATION


# 2: AGE ==================================================================================================================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot_send_data(update, get_text(s.WHAT_AGE))


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = int(update.message.text)
    if age >= s.AGE_LIMIT:
        context.user_data[s.AGE] = age
        await get_location(update, context)
    else:
        context.user_data[s.TEXT_SAY_BY] = get_text(s.REFUSAL)
        await bot_say_by(update, context)


# 3: NAVIGATION ==================================================================================================================
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    initiate_user_data(context)
    add_backwards(context, s.AGE)
    text, keyboard = controls.get_init()
    await bot_send_data(update, text, keyboard)


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "init")
    text, keyboard = controls.get_country()
    await bot_send_data(update, text, keyboard)


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "init")
    text, keyboard = await controls.get_region()
    await bot_send_data(update, text, keyboard)


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_region=None):
    if parent_region is None:
        parent_region = controls.set_location(
            update, cbq.GET_CITY, s.REGION, context)
        add_backwards(context, check_region_for_exceptions(parent_region))
    text, keyboard = await controls.get_city(parent_region)
    await bot_send_data(update, text, keyboard)


async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_city=None):
    age = context.user_data.get(s.AGE, 17)
    if parent_city is None:
        parent_city = controls.set_location(
            update, cbq.GET_FUND, s.CITY, context)
        add_backwards(context, check_city_for_exceptions(parent_city))
    text, keyboard = await controls.get_fund(parent_city, age)
    await bot_send_data(update, text, keyboard)


# 4: FUNDS ==================================================================================================================
async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = controls.get_info(s.FUNDS_DESCRIPTION, cbq.GET_FUND)
    await bot_send_data(update, text, keyboard)


async def fund_missing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, controls.parse_data(update, cbq.NO_FUND))
    text, keyboard = controls.get_fund_missing()
    await bot_send_data(update, text, keyboard)


async def get_new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=s.PRESS_BUTTON_TO_FILL_FORM,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                s.FILL_FORM_BUTTON_TEXT,
                web_app=WebAppInfo(url="https://procharity.ru/"),
            )
        ),
    )
    # return s.NEW_FUND


async def get_application_started(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    add_backwards(context, "fund")
    context.user_data["fund"] = controls.parse_data(update, cbq.GET_APPLICATION_STARTED)
    text, keyboard = controls.get_application_started()
    await bot_send_data(update, text, keyboard)


# === APPLICATION TO GOOGLE ===================================================================================================
CHECK_FIO = "check_fio"
CHECK_EMAIL = "check_email"
TEST_TEXT_GET_FIO = " Фамилия Имя Отчество"
TEST_TEXT_GET_EMAIL = "mail@yandex.ru +7(921)xxx-xx-xx Программист"
FIO = "fio"
EMAIL = "email"
DEFAULT_INPUT_FIO = "Surname Name Patronimic"
DEFAULT_INPUT_EMAIL = "Email Phone Profession"
TEXT_ERROR_INPUT = "{}, ты немного ошибся при вводе своих данных, можем повторить )))"
FIO_OUTPUT = s.BOT_SPEAKING + "{}, твои ФИО:\n\nФамилия: {}\nИмя: {}\n Отчество: {}"
EMAIL_OUTPUT = s.BOT_SPEAKING + "{}, твои данные:\n\nE-mail: {}\nТелефон: {}\n Профессия: {}"
TEST_DATA_FOR_GOOGLE = [
    ["first_row"],
    ["second_row"],
]


async def send_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    send_to_google_sheets(TEST_DATA_FOR_GOOGLE)
    # text = "{}, ваши данные успешно отправлены"
    # keyboard = get_markup_OK("init")
    # text, keyboard = controls.get_info("{}, ваши данные успешно отправлены", cbq.GET_LOCATION)
    # await message(update, text, keyboard)


# === BACWARDS =============================================================================================================
async def backwards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        category = context.user_data.get(cbq.STACK).pop()
    except IndexError:
        await get_location(update, context)
    else:
        match category:
            case s.AGE: await get_age(update, context)
            case "init": await get_location(update, context)
            case "country": await get_country(update, context)
            case "region": await get_region(update, context)
            case "city":
                await get_city(
                    update, context, context.user_data.get(s.REGION))
            case "fund":
                await get_fund(update, context, context.user_data.get(s.CITY))
            # case "fio": await get_fio(update, context)
            # case "email": await get_email(update, context)


# === WebApp ============================================================================================
async def get_final_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    KEY_ERROR_MESSAGE = "Test data"
    data = context.user_data
    text = s.BOT_SPEAKING + (
        f"{s.USERNAME}, твои данные будут отправлены:\n\n"
        f"Фамилия:      {data.get('surname', KEY_ERROR_MESSAGE)}\n"
        f"Имя:          {data.get('name', KEY_ERROR_MESSAGE)}\n"
        f"Отчество:     {data.get('patronimic', KEY_ERROR_MESSAGE)}\n"
        f"Возраст:      {data.get('age', KEY_ERROR_MESSAGE)}\n"
        f"Регион:       {data.get('region', 'Нет региона')}\n"
        f"Город:        {data.get('city', 'Нет города')}\n"
        f"Профессия:    {data.get('occupation', KEY_ERROR_MESSAGE)}\n"
        f"E-mail:       {data.get('email', KEY_ERROR_MESSAGE)}\n"
        f"Телефон:      {data.get('phone', KEY_ERROR_MESSAGE)}\n"
        f"Фонд:         {data.get('fund', KEY_ERROR_MESSAGE)}\n\n"
    )
    context.user_data[s.TEXT_SAY_BY] = " Так бывает "
    add_backwards(context, "fund")
    footer = [
        get_args_back("Изменить фонд", cbq.GET_FUND),
        (s.EXIT_EMOJI + "Выход?", cbq.SAY_BY),
        (s.TEXT_FINISH, cbq.SEND_SPREADSHEET),
    ]
    keyboard = get_keyboard(footer=footer)
    # send_to_google_sheets(TEST_DATA_FOR_GOOGLE)
    await bot_send_data(update, text, keyboard)


async def get_new_application_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=s.PRESS_BUTTON_TO_FILL_FORM,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                s.FILL_FORM_BUTTON_TEXT,
                web_app=WebAppInfo(url=WEBAPP_HTML),
            )
        ),
    )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""
    '''data = json.loads(update.effective_message.web_app_data.data)
    await update.message.reply_html(
        text=f"{data.get('surname', 'SURNAME IS NONE')}",
        reply_markup=ReplyKeyboardRemove(),
    )'''
    KEY_ERROR_MESSAGE = "***"
    data = json.loads(update.effective_message.web_app_data.data)
    context.user_data["surname"] = data.get("surname", KEY_ERROR_MESSAGE)
    context.user_data["name"] = data.get("name", KEY_ERROR_MESSAGE)
    context.user_data["patronimic"] = data.get("patronimic", KEY_ERROR_MESSAGE)
    context.user_data["email"] = data.get("email", KEY_ERROR_MESSAGE)
    context.user_data["phone"] = data.get("phone_number", KEY_ERROR_MESSAGE)
    context.user_data["occupation"] = data.get("occupation", KEY_ERROR_MESSAGE)
        #
        # context.user_data["fund"] = data.get("fund", KEY_ERROR_MESSAGE)
        # context.user_data["age"] = data.get("age", KEY_ERROR_MESSAGE)
        # context.user_data["region"] = data.get("region", KEY_ERROR_MESSAGE)
        # context.user_data["city"] = data.get("city", KEY_ERROR_MESSAGE)
    '''await update.message.reply_html(
        text=f"You selected the color with the HEX value <code>{data['surname']}</code>. The "
        f"corresponding RGB value is <code>{data['name'].values()}</code>.",
        reply_markup=ReplyKeyboardRemove(),
    )'''
    await get_final_confirmation(update, context)
# =============================================================================================


# 5: CONVERSATION ==================================================================================================================
HANDLERS = (
    ConversationHandler(
        entry_points=[CommandHandler("start", greetings)],

        states={
            s.MAIN_CONVERSATION: [
                CallbackQueryHandler(get_age, cbq.GET_AGE),
                MessageHandler(filters.Regex(r"^\d{1,3}$"), check_age),
                CallbackQueryHandler(bot_say_by, cbq.SAY_BY),
                CallbackQueryHandler(get_location, cbq.GET_LOCATION),
                CallbackQueryHandler(get_region, cbq.GET_REGION),
                CallbackQueryHandler(get_country, cbq.GET_COUNTRY),
                CallbackQueryHandler(get_city, is_city_requested),
                CallbackQueryHandler(get_fund, is_fund_requested),
                CallbackQueryHandler(backwards, is_backwards_requested),
                CallbackQueryHandler(get_funds_info, cbq.GET_FUNDS_INFO),
                CallbackQueryHandler(fund_missing, cbq.NO_FUND),
                CallbackQueryHandler(get_new_fund_form, cbq.GET_NEW_FUND_FORM),
                CallbackQueryHandler(get_application_started, cbq.GET_APPLICATION_STARTED),
                CallbackQueryHandler(get_new_application_form, cbq.NEW_APPLICATION_FORM),
                # CallbackQueryHandler(get_final_confirmation, cbq.GET_FINAL_CONFIRMATION),
                CallbackQueryHandler(send_spreadsheet, cbq.SEND_SPREADSHEET),
                MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data)
                # CallbackQueryHandler(check_fio, CHECK_FIO),
                # CallbackQueryHandler(get_email, cbq.GET_EMAIL),
                # CallbackQueryHandler(check_email, CHECK_EMAIL),
                # MessageHandler(filters.TEXT, check_fio),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)


'''async def get_user_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text_: str,
    callback_query: str,
    user_data_key: str,
    user_data_value: str,
):
    # add_backwards(context, "fio")
    # to be replaced with user input
    context.user_data[user_data_key] = user_data_value
    text = get_text(text_)
    keyboard = get_markup_OK(callback_query)
    await bot_send_data(update, text, keyboard)


async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_user_input(
        update, context, s.TEXT_GET_FIO,
        CHECK_FIO, FIO, TEST_TEXT_GET_FIO,
    )


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await get_user_input(
        update, context, s.TEXT_GET_EMAIL,
        CHECK_EMAIL, EMAIL, TEST_TEXT_GET_EMAIL,
    )


def is_user_input_valid(data) -> bool:
    return len(data) == 3
    # needs more cases


async def check_user_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    user_data_key: str,  # FIO or EMAIL
    default_input: str,
    keys_for_saving: tuple[str],
    callback_query: str,
    backwards: str | None = None
):
    # === PARSING ===
    # fio = update.message.text.split()
    raw_data = context.user_data.get(user_data_key, default_input).split(" ")
    # === VALIDATION ===
    if is_user_input_valid(raw_data):
        key1, key2, key3 = keys_for_saving
        value1, value2, value3 = raw_data
        context.user_data[key1] = value1
        context.user_data[key2] = value2
        context.user_data[key3] = value3
        text = text.format(s.USERNAME, value1, value2, value3)
    else:
        text = get_text(TEXT_ERROR_INPUT)
    # === CONTROLS ===
    add_backwards(context, user_data_key if backwards is None else backwards)
    footer = [get_args_back("Опечатка"), get_args_ahead(callback_query=callback_query)]
    keyboard = get_keyboard(footer=footer)
    await bot_send_data(update, text, keyboard)


async def check_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_user_input(
        update, context, FIO_OUTPUT, FIO, DEFAULT_INPUT_FIO,
        ("surname", "name", "patronimic"), cbq.GET_EMAIL,
    )


async def check_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await check_user_input(
        update, context, EMAIL_OUTPUT, EMAIL, DEFAULT_INPUT_EMAIL,
        ("email", "phone", "profession"), cbq.QUERY_FINAL_CONFIRMATION,
    )'''

'''async def check_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "fio")
    # text = get_text(s.TEXT_GET_PROFESSION)
    text = s.TEXT_GET_EMAIL
    # context.user_data["profession"] = "Sailor, just a Sailor"
    buttons = get_button_row(
        get_back_button("Что-то не заладилось"),
        ("Далее" + s.GO_RIGHT, s.QUERY_FINAL_CONFIRMATION),
        # ("Далее" + s.GO_RIGHT, cbq.GET_EMAIL),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)


async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "email")
    text = get_text(s.TEXT_GET_PHONE_NUMBER)
    buttons = get_button_row(  # to change for get_row_buttons which name is more logical and explicit
        get_back_button("Almost no way back"),
        ("Далее" + s.GO_RIGHT, s.QUERY_FINAL_CONFIRMATION),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)'''
'''    # === PARSING ===
    # fio = update.message.text.split()
    email_raw = context.user_data.get(, ).split(" ")
    # === VALIDATION ===
    if len(email_raw) != 3:
        text = f"{s.USERNAME}, ты немного ошибся при вводе своих данных, можем повторить )))"
    else:
        email, phone, profession = email_raw
        context.user_data["profession"] = profession
        context.user_data["phone"] = phone
        context.user_data["email"] = email
        text = s.BOT_SPEAKING + f"
    # === SENDING CARD ===
    add_backwards(context, "email")
    buttons = get_button_row(
        get_back_button("Опечатка"),
        ("Далее" + s.GO_RIGHT, cbq.QUERY_FINAL_CONFIRMATION),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)'''

'''
# === CONTROLS ============================================================================
def get_init_controls() -> tuple[str, InlineKeyboardMarkup]:
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


def get_country_controls() -> tuple[str, InlineKeyboardMarkup]:
    text = s.CHOOSE_COUNTRY
    buttons = [
        (s.KAZAHSTAN + s.KAZAHSTAN_EMOJI, cbq.GET_FUND + s.COUNTRY),
        (cbq.OTHER_COUNTRY, cbq.NO_FUND + s.COUNTRY),
    ]
    footer = [get_args_back("В начало")]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_region_controls(parent_country=None):
    from .models import CoverageArea
    text = s.CHOOSE_REGION
    buttons = [
        (region.name, cbq.GET_CITY + region.name)
        async for region in
        CoverageArea.objects.filter(level=1)
        if region.name not in s.TWO_CAPITALS
    ]
    footer = [get_args_back("В начало"), (cbq.NO_MY_REGION_TEXT, cbq.NO_FUND + s.REGION)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_city_controls(parent_region):
    from .models import CoverageArea
    text = s.CHOOSE_CITY
    buttons = [
        (city.name, cbq.GET_FUND + city.name)
        async for city in
        CoverageArea.objects.filter(parent__name=parent_region)
    ]
    footer = [get_args_back(), (cbq.NO_MY_CITY_TEXT, cbq.NO_FUND + s.CITY)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_fund_controls(parent_city, age):
    # from .models import Fund
    text = s.CHOOSE_FUND
    buttons = [
        (fund.name, cbq.GET_APPLICATION_STARTED + fund.name)
        async for fund in Fund.objects.filter(
            coverage_area__name=parent_city,
            age_limit__from_age__lte=age,
        )
    ]

    buttons = [
        ("1 Арифметика добра", cbq.GET_APPLICATION_STARTED + "1 Арифметика добра"),
        ("2 Арифметика добра", cbq.GET_APPLICATION_STARTED + "2 Арифметика добра"),
        ("3 Арифметика добра", cbq.GET_APPLICATION_STARTED + "3 Арифметика добра"),
        ("4 Арифметика добра", cbq.GET_APPLICATION_STARTED + "4 Арифметика добра"),
        ("5 Арифметика добра", cbq.GET_APPLICATION_STARTED + "5 Арифметика добра"),
    ]
    footer = [get_args_back("Изменить город"), (cbq.FUNDS_INFO_TEXT, cbq.GET_FUNDS_INFO)]
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


def get_funds_info_controls():
    text = s.FUNDS_DESCRIPTION
    keyboard = get_markup_OK(cbq.GO_BACK)
    return text, keyboard


def get_fund_missing_controls():
    text = get_text(s.NO_FUND_MESSAGE)
    footer = [get_args_back(), (s.NEW_FUND_CONFIRM_MESSAGE, s.NEW_FUND_FORM)]
    keyboard = get_keyboard(footer=footer)
    return text, keyboard'''
