from urllib.parse import urljoin

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

from apps.registration.utils import read_web_app, send_to_google, webapp

from . import controls
from .bot_settings import cbq, constants, conversation, funds
from .utils import (
    add_backwards,
    bot_send_data,
    check_city_for_exceptions,
    check_region_for_exceptions,
    is_backwards_requested,
    is_city_requested,
    is_fund_requested,
    send_html,
)


def initiate_user_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    temp = context.user_data.get(constants.AGE, 17)
    context.user_data.clear()
    context.user_data[constants.COUNTRY] = "Россия"
    context.user_data[constants.AGE] = temp
    context.user_data[cbq.STACK] = []


# 1: GREETINGS ==================================================================================================================
async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await send_html(update, *controls.get_info(conversation.GREETING, cbq.GET_AGE))
    return constants.MAIN_CONVERSATION


# 2: AGE ==================================================================================================================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_send_data(update, conversation.WHAT_AGE)


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    age = update.message.text
    if int(age) < constants.AGE_LIMIT:
        await send_html(update, conversation.REFUSAL)
        return ConversationHandler.END
    context.user_data[constants.AGE] = age
    # add_backwards(context, constants.AGE) добавлять свой уровень, а при возврате два раза pop()
    return await get_location(update, context)


# 3: NAVIGATION ==================================================================================================================
async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    initiate_user_data(context)
    add_backwards(context, constants.AGE)
    # add_backwards(context, "init")  добавлять свой уровень, а при возврате два раза pop()
    await bot_send_data(update, *controls.get_init())


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, "init")
    await bot_send_data(update, *controls.get_country())


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, "init")
    text, keyboard = await controls.get_region()
    await bot_send_data(update, text, keyboard)


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_region=None) -> None:
    if parent_region is None:
        parent_region = controls.set_location(update, cbq.GET_CITY, constants.REGION, context)
        add_backwards(context, check_region_for_exceptions(parent_region))
    text, keyboard = await controls.get_city(parent_region)
    await bot_send_data(update, text, keyboard)


# 4: FUNDS ==================================================================================================================
async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE, parent_city=None) -> None:
    if parent_city is None:
        parent_city = controls.set_location(update, cbq.GET_FUND, constants.CITY, context)
        add_backwards(context, check_city_for_exceptions(parent_city))
    text, keyboard = await controls.get_fund(parent_city, context.user_data[constants.AGE])
    await bot_send_data(update, text, keyboard)


async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text, keyboard = controls.get_info(funds.DESCRIPTION, cbq.GET_FUND)
    await bot_send_data(update, text, keyboard)


async def fund_missing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, controls.parse_data(update, cbq.NO_FUND))
    text, keyboard = controls.fund_missing()
    await bot_send_data(update, text, keyboard)


'''async def get_application_started(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, "fund")
    context.user_data["fund"] = controls.parse_data(update, cbq.GET_APPLICATION_STARTED)
    text, keyboard = controls.get_application_started()
    await bot_send_data(update, text, keyboard)'''


# === WebApp ============================================================================================
async def get_new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    age = context.user_data.get(constants.AGE)
    url = urljoin(settings.APPLICATION_URL, reverse('new_fund', args=[age]))
    await webapp(update, context, url)


async def get_new_mentor_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[constants.FUND] = controls.parse_data(update, cbq.GET_NEW_MENTOR_FORM)
    age = context.user_data.get(constants.AGE)
    region = context.user_data.get(constants.REGION, ' ')
    city = context.user_data.get(constants.CITY, ' ')
    fund = context.user_data.get(constants.FUND)
    url = urljoin(settings.APPLICATION_URL, reverse('new_user', args=[age, region, city, fund]))
    await webapp(update, context, url)


async def read_webapp_send_to_google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    back = await read_web_app(update, context)
    if back is not None:
        await backwards(update, context)


# === BACWARDS =============================================================================================================
async def backwards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        category = context.user_data.get(cbq.STACK).pop()
    except IndexError:
        await get_location(update, context)
    else:
        match category:
            case constants.AGE: await get_age(update, context)
            case "init": await get_location(update, context)
            case "country": await get_country(update, context)
            case "region": await get_region(update, context)
            case "city": await get_city(
                update, context, context.user_data.get(constants.REGION))
            case "fund": await get_fund(
                update, context, context.user_data.get(constants.CITY))


# 5: CONVERSATION ==================================================================================================================
HANDLERS = (
    ConversationHandler(
        entry_points=[CommandHandler("start", greetings)],
        states={
            constants.MAIN_CONVERSATION: [
                CallbackQueryHandler(get_age, cbq.GET_AGE),
                MessageHandler(filters.Regex(r"^\d{1,3}$"), check_age),
                CallbackQueryHandler(get_location, cbq.GET_LOCATION),
                CallbackQueryHandler(get_region, cbq.GET_REGION),
                CallbackQueryHandler(get_country, cbq.GET_COUNTRY),
                CallbackQueryHandler(get_city, is_city_requested),
                CallbackQueryHandler(get_fund, is_fund_requested),
                CallbackQueryHandler(backwards, is_backwards_requested),
                CallbackQueryHandler(get_funds_info, cbq.GET_FUNDS_INFO),
                CallbackQueryHandler(fund_missing, cbq.NO_FUND),
                CallbackQueryHandler(get_new_fund_form, cbq.GET_NEW_FUND_FORM),
                # CallbackQueryHandler(get_application_started, cbq.GET_APPLICATION_STARTED),
                CallbackQueryHandler(get_new_mentor_form, cbq.GET_NEW_MENTOR_FORM),
                CallbackQueryHandler(send_to_google, cbq.SEND_SPREADSHEET),
                MessageHandler(filters.StatusUpdate.WEB_APP_DATA, read_webapp_send_to_google),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)
