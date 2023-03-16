# import json
from typing import List, Optional

from telegram import (
    InlineKeyboardMarkup,
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
    add_if_unique,
    get_keyboard,
    get_text,
    is_back,
    is_city_requested,
    is_fund_requested,
    markup_OK,
)


cbq = s.CallbackQueries
__stack: List = []


# to make bot_send_message
async def message(update: Update, text: str, reply=None):
    await update.message.reply_html(text, reply_markup=reply)


# to make as decorator later
async def bot_send_data(
    update: Update,
    text: str,
    keyboard: Optional[InlineKeyboardMarkup] = None,
    stack: bool = True,
) -> None:
    if update.message:
        await update.message.reply_html(text, reply_markup=keyboard)
    else:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, reply_markup=keyboard)
    if stack:
        add_if_unique(__stack, text, keyboard)


async def bot_say_by(update: Update, text: str) -> int:
    await message(update, text)
    return ConversationHandler.END


# 1: GREETINGS ==================================================================================================================
async def greetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[s.COUNTRY] = "Россия"
    s.USERNAME = update.message.from_user.first_name
    await update.message.reply_html(
        text=get_text(s.GREETING), reply_markup=markup_OK(cbq.GET_AGE))
    return s.MAIN_CONVERSATION


# 2: AGE ==================================================================================================================
async def get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot_send_data(update, get_text(s.WHAT_AGE), stack=False)


async def check_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    age = int(update.message.text)
    if s.AGE_LIMIT < age:
        context.user_data[s.AGE] = age
        await get_location(update, context)
    else:
        await bot_say_by(update, get_text(s.REFUSAL))


# 3: LOCATION ==================================================================================================================
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(__stack) > 1:
        __stack.pop()
        await bot_send_data(update, **__stack.pop(), stack=False)
    else:
        await get_location(update, context)


async def get_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = s.CHOOSE_COUNTRY
    buttons = [
        ("Казахстан", cbq.GET_FUND),
        ("Другая страна", cbq.NO_FUND),
    ]
    keyboard = get_keyboard(buttons, footer=cbq.LONG_BACK_BUTTON)
    await bot_send_data(update, text, keyboard)


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    __stack.clear()
    text = get_text(s.WHAT_LOCATION)
    buttons = [
        (s.MSK, cbq.GET_FUND + s.MSK),
        (s.SPB, cbq.GET_FUND + s.SPB),
        (s.MSK_reg, cbq.GET_CITY + s.MSK_reg),
        (cbq.BUTTON_OTHER_REGION),
        (cbq.BUTTON_OTHER_COUNTRY),
    ]
    keyboard = get_keyboard(buttons)
    await bot_send_data(update, text, keyboard)
    return s.MAIN_CONVERSATION


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .models import CoverageArea
    text = s.CHOOSE_REGION
    buttons = [
        (region.name, cbq.GET_CITY + region.name)
        async for region in
        CoverageArea.objects.filter(level=1)
        if region.name not in s.TWO_CAPITALS]
    footer = (
        (cbq.NO_MY_REGION_TEXT, cbq.NO_FUND),
        cbq.LONG_BACK_BUTTON)
    keyboard = get_keyboard(buttons, footer=footer)
    await bot_send_data(update, text, keyboard)


def set_location(
    data: str, prefix: str, location_name: str,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.user_data[location_name] = data.replace(prefix, "")


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_location(update.callback_query.data, cbq.GET_CITY, s.REGION, context)
    from .models import CoverageArea
    text = s.CHOOSE_CITY
    buttons = [
        (city.name, cbq.GET_FUND + city.name)
        async for city in
        CoverageArea.objects.filter(parent__name=context.user_data[s.REGION])]
    footer = (
        (cbq.NO_MY_CITY_TEXT, cbq.NO_FUND),
        cbq.LONG_BACK_BUTTON)
    keyboard = get_keyboard(buttons, footer=footer)
    await bot_send_data(update, text, keyboard)


# 4: FUNDS ==================================================================================================================
async def get_fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    set_location(update.callback_query.data, cbq.GET_FUND, s.CITY, context)
    # from .models import CoverageArea, Fund
    text = s.CHOOSE_FUND
    buttons = [
        (cbq.FUNDS_INFO_TEXT, cbq.GET_FUNDS_INFO),
        ("1 Арифметика добра", "Арифметика добра"),
        ("2 Арифметика добра", "Арифметика добра"),
        ("3 Арифметика добра", "Арифметика добра"),
    ]
    keyboard = get_keyboard(buttons, footer=cbq.LONG_BACK_BUTTON)
    await bot_send_data(update, text, keyboard)


async def get_funds_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = s.FUNDS_DESCRIPTION
    keyboard = markup_OK(cbq.GET_FUND)
    await bot_send_data(update, text, keyboard, stack=False)


async def no_fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = s.NO_FUND_MESSAGE.format(s.USERNAME)
    keyboard = get_keyboard([(s.NEW_FUND_CONFIRM_MESSAGE, s.NEW_FUND_FORM)])
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
                CallbackQueryHandler(go_back, is_back),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)


'''

# CallbackQueryHandler(get_fund, cbq.GET_FUND),

CallbackQueryHandler(send_error, is_invalid_data),

def is_invalid_data(data):
    return True if isinstance(data, InvalidCallbackData) else False


async def send_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(
        text=get_text(update.callback_query.data), reply_markup=markup_OK(cbq.GET_AGE))




# CallbackQueryHandler(check_country, cbq.CHECK_COUNTRY),

async def check_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[s.COUNTRY] = update.callback_query.data
    if update.callback_query.data == "Казахстан":
        return await get_fund(update, context)




        (fund.name, cbq.CHECK_FUND + fund.name)
        async for fund in Fund.objects.filter(
        age_limit__from_age<=age)
        # CoverageArea.objects.funds.all()






async def check_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[s.CITY] = update.callback_query.data
    return await get_fund(update, context)


async def check_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[s.REGION] = update.callback_query.data
    if update.callback_query.data not in (s.TWO_CAPITALS):
        return await city(update, context)
    return await fund(update, context)


async def check_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from .models import CoverageArea
    context.user_data[s.CITY] = update.callback_query.data
    region_from_mtpp = await CoverageArea.objects.aget(name=context.user_data[s.REGION])
    city_from_mtpp = await CoverageArea.objects.aget(name=context.user_data[s.CITY])
    if region_from_mtpp.id == city_from_mtpp.parent_id:
        return await get_fund(update, context)
    return ConversationHandler.END









async def read_new_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    json.loads(update.effective_message.web_app_data.data)
    # TODO: передать данные из формы в google таблицу
    await update.message.reply_html(
        text=s.START_PROJECT_REQUEST,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def check_fund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[s.FUND] = {s.NAME: update.callback_query.data}
    if update.callback_query.data == "Арифметика добра":
        context.user_data[s.FUND][s.URL] = "https://crm.a-dobra.ru/form/mentor"
    if context.user_data[s.FUND].get(s.URL):
        return await fund_has_form(update, context)
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "Последний шаг - заполним анкету",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Изменить фонд", callback_data="fund")],
                [InlineKeyboardButton("Заполнить анкету", callback_data="fund_form")],
            ]
        ),
    )
    return s.FUND


async def fund_has_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "У этого фонда есть своя анкета, заполни ее на сайте фонда по ссылке " f"{context.user_data[s.FUND][s.URL]}"
    )
    return ConversationHandler.END


async def fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Нажмите на кнопку ниже, чтобы заполнить анкету",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                "Заполнить анкету",
                # TODO: заменить на веб-приложение с формой
                # Данные для подстановки в форму:
                # context.user_data[AGE] - возраст
                # context.user_data[COUNTRY] - страна
                # context.user_data[REGION] - регион, если есть
                # context.user_data[CITY] - город, если есть
                # context.user_data[FUND][NAME] - название фонда
                web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"),
            )
        ),
    )
    return s.FUND


async def read_fund_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    print("web_app data:", data)  # FIXME: удалить
    # TODO: передать данные из формы в google таблицу
    await update.message.reply_html(
        "Спасибо! Я передал твою заявку. Фонд свяжется с тобой, чтобы "
        "уточнить детали и пригласить на собеседование.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
'''


'''
HANDLERS = (
    ConversationHandler(
        entry_points=[CommandHandler("start", greetings)],
        states={
            s.AGE: [
                CallbackQueryHandler(age, s.AGE),  # "^age$"),
                MessageHandler(filters.Regex(r"^\d{1,3}$"), check_age),
            ],
            s.LOCATION: [
                CallbackQueryHandler(region, s.OTHER_CITY),  # "^other_city$"),
                CallbackQueryHandler(country, s.OTHER_COUNTRY),  # "^other_country$"),
                CallbackQueryHandler(check_location),  # , "^.*$"),
            ],
            s.COUNTRY: [
                CallbackQueryHandler(no_fund, "^no_fund$"),
                CallbackQueryHandler(country, "^next|prev$"),
                CallbackQueryHandler(check_country, "^.*$"),
            ],
            s.REGION: [
                CallbackQueryHandler(no_fund, "^no_fund$"),
                CallbackQueryHandler(region, "^next|prev$"),
                CallbackQueryHandler(check_region, "^.*$"),
            ],
            s.CITY: [
                CallbackQueryHandler(no_fund, "^no_fund$"),
                CallbackQueryHandler(city, "^next|prev$"),
                CallbackQueryHandler(check_city, "^.*$"),
            ],
            s.FUND: [
                CallbackQueryHandler(location, "^change_city$"),
                CallbackQueryHandler(funds_info, "^info$"),
                CallbackQueryHandler(fund, "^next|prev|fund$"),
                CallbackQueryHandler(fund_form, "^fund_form$"),
                CallbackQueryHandler(check_fund, "^.*$"),
                MessageHandler(filters.StatusUpdate.WEB_APP_DATA, read_fund_form),
            ],
            s.NEW_FUND: [
                CallbackQueryHandler(new_fund_form, "^new_fund_form$"),
                MessageHandler(
                    filters.StatusUpdate.WEB_APP_DATA,
                    read_new_fund_form,
                ),
            ],
        },
        fallbacks=[CommandHandler("start", greetings)],
    ),
)





    if update.callback_query.data == s.MSK:
        context.user_data[s.REGION] = s.MSK_reg
        context.user_data[s.CITY] = s.MSK  # update.callback_query.data
        return await fund(update, context)
    elif update.callback_query.data == s.MSK_reg:
        context.user_data[s.REGION] = s.MSK_reg
        context.user_data[s.CITY] = s.MSK_reg  # update.callback_query.data
        return await fund(update, context)
    elif update.callback_query.data == s.SPB:
        context.user_data[s.REGION] = s.SPB  # update.callback_query.data
        context.user_data[s.CITY] = s.SPB  # update.callback_query.data
        return await fund(update, context)
    else:
        context.user_data[s.REGION] = update.callback_query.data
        return await region(update, context)
'''
