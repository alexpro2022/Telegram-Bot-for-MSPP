import json

from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import ContextTypes, ConversationHandler

from apps.bot import bot_settings as s
from apps.bot import controls
from apps.bot.utils import add_backwards, bot_send_data

cbq = s.CallbackQueries


async def webapp(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str,
    message_text: str = "Нажми на кнопку ниже, чтобы заполнить анкету",
    button_text: str = "Заполнить анкету",
) -> None:
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message_text,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(button_text, web_app=WebAppInfo(url=url))))
'''reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(button_text, web_app=WebAppInfo(url=url))]],
            one_time_keyboard=True,
        ))'''


async def read_web_app(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> str | None:
    data = json.loads(update.effective_message.web_app_data.data)
    # if telegram BackButton was clicked:
    back = data.get("back")
    if back is not None:
        return back
    # else fill the context.user_data with webapp data
    for key in data.keys():
        context.user_data[key] = data[key]
    # and get the final confirmation
    add_backwards(context, "fund")
    text, keyboard = controls.get_confirmation(context.user_data)
    return await bot_send_data(update, text, keyboard)


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
