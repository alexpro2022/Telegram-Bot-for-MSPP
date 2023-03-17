# import json
# from typing import List, Optional

from telegram import (
    # InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    # ReplyKeyboardRemove,
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

from . import bot_settings as s

from .utils import (
    add_backwards,
    bot_say_by,
    bot_send_data,
    check_city_for_exceptions,
    check_region_for_exceptions,
    get_keyboard,
    get_text,
    initiate_user_data,
    is_backwards_requested,
    is_city_requested,
    is_fund_requested,
    markup_OK,
)


cbq = s.CallbackQueries


# 1: GREETINGS ==================================================================================================================
async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s.USERNAME = update.message.from_user.first_name
    await update.message.reply_html(
        text=get_text(s.GREETING), reply_markup=markup_OK(cbq.GET_AGE))
    return s.MAIN_CONVERSATION


# 2: AGE ==================================================================================================================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot_send_data(update, get_text(s.WHAT_AGE))


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = int(update.message.text)
    if s.AGE_LIMIT < age:
        context.user_data[s.AGE] = age
        await get_location(update, context)
    else:
        await bot_say_by(update, get_text(s.REFUSAL))


# === CONTROLS ============================================================================
def get_init_controls():
    text = get_text(s.WHAT_LOCATION)
    buttons = [
        (s.MSK, cbq.GET_FUND + s.MSK),
        (s.SPB, cbq.GET_FUND + s.SPB),
        (s.MSK_reg, cbq.GET_CITY + s.MSK_reg),
        (cbq.BUTTON_OTHER_REGION),
        (cbq.BUTTON_OTHER_COUNTRY),
    ]
    keyboard = get_keyboard(buttons)
    return text, keyboard


def get_country_controls():
    text = s.CHOOSE_COUNTRY
    buttons = [
        (s.KAZAHSTAN, cbq.GET_FUND + s.COUNTRY),  # "country"),  # s.KAZAHSTAN),
        # cbq.BUTTON_OTHER_COUNTRY_NO_FUND,
        (cbq.OTHER_COUNTRY, cbq.NO_FUND + s.COUNTRY),
    ]
    keyboard = get_keyboard(buttons, footer=cbq.LONG_BACK_BUTTON)
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
    footer = (
        (cbq.NO_MY_REGION_TEXT, cbq.NO_FUND + s.REGION),
        cbq.LONG_BACK_BUTTON
    )
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
    footer = (
        (cbq.NO_MY_CITY_TEXT, cbq.NO_FUND + s.CITY),
        cbq.LONG_BACK_BUTTON
    )
    keyboard = get_keyboard(buttons, footer=footer)
    return text, keyboard


async def get_fund_controls(parent_city, age):
    # from .models import CoverageArea, Fund
    text = s.CHOOSE_FUND
    buttons = [
        (cbq.FUNDS_INFO_TEXT, cbq.GET_FUNDS_INFO),
        ("1 Арифметика добра", "Арифметика добра"),
        ("2 Арифметика добра", "Арифметика добра"),
        ("3 Арифметика добра", "Арифметика добра"),
    ]
    keyboard = get_keyboard(buttons, footer=cbq.LONG_BACK_BUTTON)
    return text, keyboard


# === PARSING =================================================================================================================
def parse_data(data: str, prefix: str) -> str:
    return data.replace(prefix, "")


def set_location(
    data: str, prefix: str, location_name: str,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.user_data[location_name] = parse_data(data, prefix)
    return context.user_data[location_name]


# 3: LOCATION ==================================================================================================================
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    initiate_user_data(context)
    text, keyboard = get_init_controls()
    await bot_send_data(update, text, keyboard)
    # return s.MAIN_CONVERSATION


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
            update.callback_query.data, cbq.GET_CITY, s.REGION, context)
        add_backwards(context, check_region_for_exceptions(parent_region))
    text, keyboard = await get_city_controls(parent_region)
    await bot_send_data(update, text, keyboard)


async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_city=None):
    age = context.user_data.get(s.AGE, 18)
    if parent_city is None:
        parent_city = set_location(
            update.callback_query.data, cbq.GET_FUND, s.CITY, context)
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
        [[cbq.LONG_BACK_BUTTON, (s.NEW_FUND_CONFIRM_MESSAGE, s.NEW_FUND_FORM), ]]
    )
    await bot_send_data(update, text, keyboard)


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
    return s.NEW_FUND


# === BACWARDS =============================================================================================================
async def backwards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        category = context.user_data.get(cbq.STACK).pop()
    except IndexError:
        await get_location(update, context)
    else:
        match category:
            case "init": await get_location(update, context)
            case "country": await get_country(update, context)
            case "region": await get_region(update, context)
            case "city":
                await get_city(
                    update, context,
                    context.user_data.get(s.REGION))
            case "fund":
                await get_fund(
                    update, context,
                    context.user_data.get(s.CITY))


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
                CallbackQueryHandler(new_fund_form, s.NEW_FUND_FORM),
                CallbackQueryHandler(backwards, is_backwards_requested),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)
