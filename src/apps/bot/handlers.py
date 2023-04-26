from django.conf import settings
from django.urls import reverse

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from . import bot_settings as s
from . import controls
from .utils import (
    add_backwards,
    bot_send_data,
    bot_say_by,
    check_city_for_exceptions,
    check_region_for_exceptions,
    get_text,
    is_backwards_requested,
    is_city_requested,
    is_fund_requested,
    message,
    set_text_by,
    set_username,
)
from apps.registration.utils import (
    read_web_app,
    send_to_google,
    webapp,
)

cbq = s.CallbackQueries


def initiate_user_data(context: ContextTypes.DEFAULT_TYPE):
    temp = context.user_data.get(s.AGE, 17)
    context.user_data.clear()
    context.user_data[s.COUNTRY] = "Россия"
    context.user_data[s.AGE] = temp
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
        context.user_data[s.AGE] = str(age)
        await get_location(update, context)
    else:
        set_text_by(context, get_text(s.REFUSAL))
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


# 4: FUNDS ==================================================================================================================
async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_city=None):
    age = int(context.user_data.get(s.AGE, "17"))
    if parent_city is None:
        parent_city = controls.set_location(
            update, cbq.GET_FUND, s.CITY, context)
        add_backwards(context, check_city_for_exceptions(parent_city))
    text, keyboard = await controls.get_fund(parent_city, age)
    await bot_send_data(update, text, keyboard)


async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text, keyboard = controls.get_info(s.FUNDS_DESCRIPTION, cbq.GET_FUND)
    await bot_send_data(update, text, keyboard)


async def fund_missing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_backwards(context, controls.parse_data(update, cbq.NO_FUND))
    text, keyboard = controls.get_fund_missing()
    await bot_send_data(update, text, keyboard)


async def get_application_started(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    add_backwards(context, "fund")
    context.user_data["fund"] = controls.parse_data(update, cbq.GET_APPLICATION_STARTED)
    text, keyboard = controls.get_application_started()
    await bot_send_data(update, text, keyboard)


# === WebApp ============================================================================================
async def get_new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = context.user_data.get(s.AGE)
    WEBAPP_URL_NEW_FUND = f"https://{settings.DOMAIN}{reverse('new_fund', args=[age])}"
    await webapp(update, context, WEBAPP_URL_NEW_FUND)


async def get_new_user_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    AGE = context.user_data.get(s.AGE)
    REGION = context.user_data.get(s.REGION, ' ')
    CITY = context.user_data.get(s.CITY, ' ')
    FUND = context.user_data.get(s.FUND)
    WEBAPP_URL_USER = f"https://{settings.DOMAIN}{reverse('new_user', args=[AGE, REGION, CITY, FUND])}"
    await webapp(update, context, WEBAPP_URL_USER)


async def read_webapp_send_to_google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    back = await read_web_app(update, context)
    if back is not None:
        await backwards(update, context)


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
                CallbackQueryHandler(get_new_user_form, cbq.NEW_APPLICATION_FORM),
                CallbackQueryHandler(send_to_google, cbq.SEND_SPREADSHEET),
                MessageHandler(filters.StatusUpdate.WEB_APP_DATA, read_webapp_send_to_google),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)
