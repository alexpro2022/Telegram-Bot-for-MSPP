from typing import Union

from telegram import (
    # KeyboardButton,
    # ReplyKeyboardMarkup,
    Update,
    # WebAppInfo,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from . import bot_settings as s

from .utils import (
    add_backwards,
    bot_send_data,
    check_city_for_exceptions,
    check_region_for_exceptions,
    get_back_button,
    get_button_row,
    get_keyboard,
    get_text,
    initiate_user_data,
    is_backwards_requested,
    is_city_requested,
    is_fund_requested,
    markup_OK,
    message,
)


cbq = s.CallbackQueries


# 1: GREETINGS ==================================================================================================================
async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s.USERNAME = update.message.from_user.first_name
    await message(update, get_text(s.GREETING), markup_OK(cbq.GET_AGE))
    return s.MAIN_CONVERSATION


# 2: AGE ==================================================================================================================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot_send_data(update, get_text(s.WHAT_AGE))


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = int(update.message.text)
    if s.AGE_LIMIT <= age:
        context.user_data[s.AGE] = age
        await get_location(update, context)
    else:
        context.user_data["text_say_by"] = get_text(s.REFUSAL)
        await bot_say_by(update, context)


# === CONTROLS ============================================================================
def get_init_controls():
    text = get_text(s.WHAT_LOCATION)
    buttons = [
        (s.MSK + s.MOSCOW_EMOJI, cbq.GET_FUND + s.MSK),
        (s.SPB + s.RAINING_EMOJI, cbq.GET_FUND + s.SPB),
        (s.MSK_reg + s.MOSCOW_REGION_EMOJI, cbq.GET_CITY + s.MSK_reg),
        (cbq.BUTTON_OTHER_REGION),
        (cbq.BUTTON_OTHER_COUNTRY),
    ]
    keyboard = get_keyboard(buttons, footer=get_back_button("Изменить возраст"))
    return text, keyboard


def get_country_controls():
    text = s.CHOOSE_COUNTRY
    buttons = [
        (s.KAZAHSTAN + s.KAZAHSTAN_EMOJI, cbq.GET_FUND + s.COUNTRY),
        (cbq.OTHER_COUNTRY, cbq.NO_FUND + s.COUNTRY),
    ]
    keyboard = get_keyboard(buttons, footer=get_back_button("В начало"))
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
    footer = ([[
        get_back_button("В начало"),
        (cbq.NO_MY_REGION_TEXT, cbq.NO_FUND + s.REGION), ]])
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
    footer = ([[
        get_back_button(),
        (cbq.NO_MY_CITY_TEXT, cbq.NO_FUND + s.CITY), ]])
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_fund_controls(parent_city, age):
    # from .models import Fund
    text = s.CHOOSE_FUND
    '''buttons = [
        (fund.name, cbq.GET_APPLICATION_STARTED + fund.name)
        async for fund in Fund.objects.filter(
            coverage_area__name=parent_city,
            age_limit__from_age__lte=age,
        )
    ]
    '''
    buttons = [
        ("1 Арифметика добра", cbq.GET_APPLICATION_STARTED + "1 Арифметика добра"),
        ("2 Арифметика добра", cbq.GET_APPLICATION_STARTED + "2 Арифметика добра"),
        ("3 Арифметика добра", cbq.GET_APPLICATION_STARTED + "3 Арифметика добра"),
        ("4 Арифметика добра", cbq.GET_APPLICATION_STARTED + "4 Арифметика добра"),
        ("5 Арифметика добра", cbq.GET_APPLICATION_STARTED + "5 Арифметика добра"),
    ]
    footer = ([[
        get_back_button("Изменить город"),
        (cbq.FUNDS_INFO_TEXT, cbq.GET_FUNDS_INFO), ]])
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


# === PARSING =================================================================================================================
def parse_data(data: str, prefix: str) -> str:
    return data.replace(prefix, "")


def set_location(
    data: Union[str, Update], prefix: str, location_name: str,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    if isinstance(data, Update):
        data = data.callback_query.data
    context.user_data[location_name] = parse_data(data, prefix)
    return context.user_data[location_name]


# 3: LOCATION ==================================================================================================================
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    initiate_user_data(context)
    add_backwards(context, s.AGE)
    text, keyboard = get_init_controls()
    await bot_send_data(update, text, keyboard)


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "init")
    text, keyboard = get_country_controls()
    await bot_send_data(update, text, keyboard)


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "init")
    text, keyboard = await get_region_controls()
    await bot_send_data(update, text, keyboard)


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_region=None):
    if parent_region is None:
        parent_region = set_location(
            update, cbq.GET_CITY, s.REGION, context)
        add_backwards(context, check_region_for_exceptions(parent_region))
    text, keyboard = await get_city_controls(parent_region)
    await bot_send_data(update, text, keyboard)


async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_city=None):
    age = context.user_data.get(s.AGE, 18)
    if parent_city is None:
        parent_city = set_location(
            update, cbq.GET_FUND, s.CITY, context)
        add_backwards(context, check_city_for_exceptions(parent_city))
    text, keyboard = await get_fund_controls(parent_city, age)
    await bot_send_data(update, text, keyboard)


# 4: FUNDS ==================================================================================================================
async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "fund")
    text = s.FUNDS_DESCRIPTION
    keyboard = markup_OK(cbq.GO_BACK)
    await bot_send_data(update, text, keyboard)


async def no_fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, parse_data(update.callback_query.data, cbq.NO_FUND))
    text = s.NO_FUND_MESSAGE.format(s.USERNAME)
    keyboard = get_keyboard(
        get_button_row(
            get_back_button(), (s.NEW_FUND_CONFIRM_MESSAGE, s.NEW_FUND_FORM)))
    await bot_send_data(update, text, keyboard)


async def get_application_started(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "fund")
    text = get_text(s.APPLICATION_FORM_TEXT)
    buttons = get_button_row(
        get_back_button("Изменить фонд"),
        (s.TEXT_NEW_APPLICATION, cbq.GET_FIO),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)
# === ABOVE WORKS =============================================================================


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
            case "fio": await get_fio(update, context)
            # case "profession": await get_email(update, context)
            case "email": await get_email(update, context)


# === APPLICATION ===================================================================================================
CHECK_FIO = "check_fio"
CHECK_EMAIL = "check_email"


async def get_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "fund")
    _to_be_replaced_with_const = s.BOT_SPEAKING + "{}, укажи через пробел: Фамилия Имя Отчество"
    text = get_text(_to_be_replaced_with_const)
    context.user_data["fio"] = "Проскуряков Алексей Анатольевич"
    await bot_send_data(update, text, keyboard=markup_OK(CHECK_FIO))


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, "fio")
    text = get_text(s.TEXT_GET_EMAIL)
    context.user_data["email"] = "alexpro1972@yandex.ru +7(921)345-24-02 Программист"
    await bot_send_data(update, text, keyboard=markup_OK(CHECK_EMAIL))


async def check_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # === PARSING ===
    # fio = update.message.text.split()
    fio = context.user_data.get("fio", "Surname Name Patronimic").split(" ")
    # === VALIDATION ===
    if len(fio) != 3:
        text = f"{s.USERNAME}, ты немного ошибся при вводе своих данных, можем повторить )))"
    else:
        surname, name, patronimic = fio
        context.user_data["surname"] = surname
        context.user_data["name"] = name
        context.user_data["patronimic"] = patronimic
        text = s.BOT_SPEAKING + f"{s.USERNAME}, твои ФИО:\n\nФамилия: {surname}\nИмя: {name}\n Отчество: {patronimic}"
    # === SENDING CARD ===
    add_backwards(context, "fio")
    buttons = get_button_row(
        get_back_button("Опечатка"),
        ("Далее" + s.GO_RIGHT, cbq.GET_EMAIL),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)


async def check_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # === PARSING ===
    # fio = update.message.text.split()
    email_raw = context.user_data.get("email", "Email Phone Profession").split(" ")
    # === VALIDATION ===
    if len(email_raw) != 3:
        text = f"{s.USERNAME}, ты немного ошибся при вводе своих данных, можем повторить )))"
    else:
        email, phone, profession = email_raw
        context.user_data["profession"] = profession
        context.user_data["phone"] = phone
        context.user_data["email"] = email
        text = s.BOT_SPEAKING + f"{s.USERNAME}, твои данные:\n\nE-mail: {email}\nТелефон: {phone}\n Профессия: {profession}"
    # === SENDING CARD ===
    add_backwards(context, "email")
    buttons = get_button_row(
        get_back_button("Опечатка"),
        ("Далее" + s.GO_RIGHT, cbq.QUERY_FINAL_CONFIRMATION),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)


async def get_final_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surname = context.user_data["surname"]
    name = context.user_data["name"]
    patronimic = context.user_data["patronimic"]
    email = context.user_data["email"]
    phone = context.user_data["phone"]
    profession = context.user_data["profession"]
    # add_backwards(context, )
    # text = get_text(s.TEXT_FINAL_CONFIRMATION)
    text = s.BOT_SPEAKING + (
        f"{s.USERNAME}, твои данные будут отправлены:\n\n"
        f"ФИО:         {surname} {name} {patronimic}\n"
        f"E-mail:      {email}\n"
        f"Телефон:     {phone}\n"
        f"Профессия:   {profession}\n"
    )
    context.user_data["text_say_by"] = "Все хорошо тебе просто нужно время, чтобы принять это решение. Надеюсь увидеть тебя вскоре"
    buttons = get_button_row(
        ("Мне самому нужен наставник", cbq.SAY_BY),
        ("Да" + s.FINISH, cbq.SEND_SPREADSHEET),
    )
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)


async def bot_say_by(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = context.user_data.get("text_say_by", "You have to impement your text in the context.user_data['text_say_by']")
    await message(update, text)
    return ConversationHandler.END


async def send_spreadsheet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


# 5: CONVERSATION ==================================================================================================================
HANDLERS = (
    ConversationHandler(
        entry_points=[CommandHandler("start", greetings)],

        states={
            s.MAIN_CONVERSATION: [
                CallbackQueryHandler(get_age, cbq.GET_AGE),
                MessageHandler(filters.Regex(r"^\d{1,3}$"), check_age),
                CallbackQueryHandler(get_location, cbq.GET_LOCATION),
                CallbackQueryHandler(get_region, cbq.GET_REGION),
                CallbackQueryHandler(get_country, cbq.GET_COUNTRY),
                CallbackQueryHandler(get_city, is_city_requested),
                CallbackQueryHandler(get_fund, is_fund_requested),
                CallbackQueryHandler(get_funds_info, cbq.GET_FUNDS_INFO),
                CallbackQueryHandler(no_fund, cbq.NO_FUND),
                CallbackQueryHandler(backwards, is_backwards_requested),
                CallbackQueryHandler(get_application_started, cbq.GET_APPLICATION_STARTED),
                CallbackQueryHandler(get_fio, cbq.GET_FIO),
                CallbackQueryHandler(check_fio, CHECK_FIO),
                CallbackQueryHandler(check_email, CHECK_EMAIL),
                CallbackQueryHandler(get_email, cbq.GET_EMAIL),
                CallbackQueryHandler(get_final_confirmation, cbq.QUERY_FINAL_CONFIRMATION),
                CallbackQueryHandler(bot_say_by, cbq.SAY_BY),
                # MessageHandler(filters.TEXT, check_fio),
                # #CallbackQueryHandler(send_spreadsheet, cbq.SEND_SPREADSHEET),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)


'''




async def new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=s.PRESS_BUTTON_TO_FILL_FORM,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                s.FILL_FORM_BUTTON_TEXT,
                # TODO: заменить на веб-приложение с формой
                # Данные для подстановки в форму:
                # context.user_data[AGE] - возраст
                web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"),
            )
        ),
    )
    return s.NEW_FUND'''
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
