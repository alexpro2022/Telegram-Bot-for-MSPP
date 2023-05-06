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
from .utils import add_backwards, bot_send_data, parse_data


# 1: GREETINGS ===============================================================
async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await bot_send_data(update, *controls.get_info(conversation.GREETING, cbq.GET_AGE))
    return constants.MAIN_CONVERSATION


# 2: AGE =====================================================================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_send_data(update, conversation.WHAT_AGE)


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    age = update.message.text
    if int(age) < constants.AGE_LIMIT:
        await bot_send_data(update, conversation.REFUSAL)
        return ConversationHandler.END
    context.user_data[constants.AGE] = age
    return await get_location(update, context)


# 3: LOCATION ================================================================
def __reset_user_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    temp = context.user_data.get(constants.AGE, 17)
    context.user_data.clear()
    context.user_data[constants.COUNTRY] = "Россия"
    context.user_data[constants.AGE] = temp
    add_backwards(context, constants.AGE)


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    __reset_user_data(context)
    add_backwards(context, constants.LOCATION)
    await bot_send_data(update, *controls.get_location())


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, constants.COUNTRY)
    await bot_send_data(update, *controls.get_country())


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, constants.REGION)
    await bot_send_data(update, *await controls.get_region())


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE, back: bool = False) -> None:
    add_backwards(context, constants.CITY)
    if not back:
        context.user_data[constants.REGION] = parse_data(update, cbq.GET_CITY)
    await bot_send_data(update, *await controls.get_city(context.user_data[constants.REGION]))


# 4: FUNDS ===================================================================
async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE, back: bool = False) -> None:
    add_backwards(context, constants.FUND)
    if not back:
        context.user_data[constants.CITY] = parse_data(update, cbq.GET_FUND)
    await bot_send_data(update, *await controls.get_fund(context.user_data[constants.CITY], context.user_data[constants.AGE]))


async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, "")
    text = conversation.BOT_SPEAKING
    for fund in parse_data(update, cbq.GET_FUNDS_INFO).split(','):
        text += funds.FUNDS.get(fund) + funds.FUNDS_INFO_SEPARATOR
    await bot_send_data(update, *controls.get_info(text, cbq.GO_BACK))


async def fund_missing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, "")
    await bot_send_data(update, *controls.fund_missing())


# === WebApp =================================================================
async def get_new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    age = context.user_data.get(constants.AGE)
    url = urljoin(settings.APPLICATION_URL, reverse('new_fund', args=[age]))
    await webapp(update, context, url)


async def get_new_mentor_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    add_backwards(context, "")
    context.user_data[constants.FUND] = parse_data(update, cbq.GET_NEW_MENTOR_FORM)
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
        context.user_data.get(cbq.STACK).pop()
        category = context.user_data.get(cbq.STACK).pop()
    except IndexError:
        await get_location(update, context)
    else:
        match category:
            case constants.AGE: await get_age(update, context)
            case constants.LOCATION: await get_location(update, context)
            case constants.COUNTRY: await get_country(update, context)
            case constants.REGION: await get_region(update, context)
            case constants.CITY: await get_city(update, context, back=True)
            case constants.FUND: await get_fund(update, context, back=True)


# 5: CONVERSATION ==================================================================================================================
HANDLERS = (
    ConversationHandler(
        entry_points=[CommandHandler("start", greetings)],
        states={
            constants.MAIN_CONVERSATION: [
                CallbackQueryHandler(backwards, cbq.GO_BACK),
                CallbackQueryHandler(get_age, cbq.GET_AGE),
                MessageHandler(filters.Regex(r"^\d{1,3}$"), check_age),
                CallbackQueryHandler(get_region, cbq.GET_REGION),
                CallbackQueryHandler(get_country, cbq.GET_COUNTRY),
                CallbackQueryHandler(get_city, cbq.GET_CITY),
                CallbackQueryHandler(get_fund, cbq.GET_FUND),
                CallbackQueryHandler(get_funds_info, cbq.GET_FUNDS_INFO),
                CallbackQueryHandler(fund_missing, cbq.NO_FUND),
                CallbackQueryHandler(get_new_fund_form, cbq.GET_NEW_FUND_FORM),
                CallbackQueryHandler(get_new_mentor_form, cbq.GET_NEW_MENTOR_FORM),
                CallbackQueryHandler(send_to_google, cbq.SEND_SPREADSHEET),
                MessageHandler(filters.StatusUpdate.WEB_APP_DATA, read_webapp_send_to_google),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)
