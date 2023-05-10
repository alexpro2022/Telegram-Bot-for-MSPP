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

from . import menu
from .bot_settings import cbq, constants, conversation, emoji
from .utils import bot_send_data, parse_data


async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    await bot_send_data(update, context, *menu.get_info(conversation.GREETING, cbq.GET_AGE), backwards=False)
    return constants.MAIN_CONVERSATION


async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_send_data(update, context, conversation.WHAT_AGE, backwards=False)


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    age = update.message.text
    if int(age) < constants.AGE_LIMIT:
        await bot_send_data(update, context, conversation.REFUSAL, backwards=False)
        return ConversationHandler.END
    context.user_data[constants.AGE] = age
    return await get_location(update, context)


def __reset_user_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    temp = context.user_data[constants.AGE]
    context.user_data.clear()
    context.user_data[constants.COUNTRY] = "Россия"
    context.user_data[constants.AGE] = temp


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    __reset_user_data(context)
    await bot_send_data(update, context, *menu.get_location())


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_send_data(update, context, *menu.get_country())


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_send_data(update, context, *await menu.get_region())


async def get_city_or_and_fund(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[constants.REGION] = parse_data(update, cbq.GET_CITY_OR_AND_FUND)
    result = await menu.get_city_or_and_fund(
        context.user_data[constants.REGION], context.user_data[constants.AGE])
    if result is None:
        return await no_fund(update, context)
    if len(result) == 3:
        context.user_data[constants.FUND_INFO] = result[2]
    return await bot_send_data(update, context, result[0], result[1])


'''async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[constants.REGION] = parse_data(update, cbq.GET_CITY)
    await bot_send_data(update, context, *await menu.get_city(context.user_data[constants.REGION]))'''


async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[constants.CITY] = parse_data(update, cbq.GET_FUND)
    text, keyboard, descriptions = await menu.get_fund(
        context.user_data[constants.CITY], context.user_data[constants.AGE])
    if keyboard is None:
        return await no_fund(update, context)
    context.user_data[constants.FUND_INFO] = descriptions
    return await bot_send_data(update, context, text, keyboard)


async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    delimeter = f"\n{emoji.GROWING_HEART*3}\n"
    text = conversation.BOT_SPEAKING
    for description in context.user_data.get(constants.FUND_INFO):
        text += delimeter + description
    await bot_send_data(update, context, *menu.get_info(text, cbq.GO_BACK))


async def no_fund(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await bot_send_data(update, context, *menu.no_fund())


async def get_new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = urljoin(settings.APPLICATION_URL, reverse('new_fund', args=[
        context.user_data.get(constants.AGE)
    ]))
    await webapp(update, context, url)


async def get_new_mentor_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[constants.FUND] = parse_data(update, cbq.GET_NEW_MENTOR_FORM)
    url = urljoin(settings.APPLICATION_URL, reverse('new_user', args=[
        context.user_data.get(constants.AGE),
        context.user_data.get(constants.REGION, ' '),
        context.user_data.get(constants.CITY, ' '),
        context.user_data.get(constants.FUND),
    ]))
    await webapp(update, context, url)


async def read_webapp_send_to_google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    back = await read_web_app(update, context)
    if back is not None:
        await backwards(update, context)


async def backwards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        context.user_data.get(cbq.CACHE).pop()
        previous = context.user_data.get(cbq.CACHE).pop()
    except IndexError:
        return await get_location(update, context)
    return await bot_send_data(update, context, *previous)


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
                CallbackQueryHandler(get_city_or_and_fund, cbq.GET_CITY_OR_AND_FUND),
                CallbackQueryHandler(get_fund, cbq.GET_FUND),
                CallbackQueryHandler(get_funds_info, cbq.GET_FUNDS_INFO),
                CallbackQueryHandler(no_fund, cbq.NO_FUND),
                CallbackQueryHandler(get_new_fund_form, cbq.GET_NEW_FUND_FORM),
                CallbackQueryHandler(get_new_mentor_form, cbq.GET_NEW_MENTOR_FORM),
                CallbackQueryHandler(send_to_google, cbq.SEND_SPREADSHEET),
                MessageHandler(filters.StatusUpdate.WEB_APP_DATA, read_webapp_send_to_google),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)
