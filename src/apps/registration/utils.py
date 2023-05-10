import json

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import ContextTypes, ConversationHandler

from apps.bot import menu
from apps.bot.bot_settings import button_text, conversation
from apps.bot.utils import add_backwards, bot_send_data


async def webapp(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str,
    message_text: str = conversation.PRESS_BUTTON_TO_FILL_FORM,
    button_text: str = button_text.FILL_FORM,
) -> None:
    keyboard = ReplyKeyboardMarkup.from_button(
        KeyboardButton(button_text, web_app=WebAppInfo(url=url)))
    await bot_send_data(update, context, message_text, keyboard, backwards=False, in_place=False)


async def read_web_app(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str | None:
    data = json.loads(update.effective_message.web_app_data.data)
    # if telegram BackButton was clicked:
    back = data.get("back")
    if back is not None:
        add_backwards(context, "fund", None)
        return back
    # else fill the context.user_data with webapp data
    for key in data.keys():
        context.user_data[key] = data[key]
    # and get the final confirmation
    return await bot_send_data(
        update, context, *menu.get_confirmation(context.user_data))


async def send_to_google(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    message_text: str = (
        "Спасибо! Я передал твою заявку. Фонд свяжется с тобой, чтобы "
        "уточнить детали и пригласить на собеседование."),
) -> int:
    form_data = context.user_data  # get_form_data_func(data)
    # google_form = AsyncGoogleFormSubmitter()
    # await google_form.submit_form(form_data)
    await update.message.reply_html(
        f"{message_text}\n{form_data}\n",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


'''reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(button_text, web_app=WebAppInfo(url=url))]],
            one_time_keyboard=True,
        ))'''
