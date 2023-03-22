import json

from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from telegram import Update, error

from .bot import bot_app
from .logger import logger


class BotWebhookView(View):
    try:

        async def post(self, request, *args, **kwargs):
            await bot_app.update_queue.put(
                Update.de_json(
                    data=json.loads(request.body),
                    bot=bot_app.bot,
                )
            )
            return JsonResponse({})

    except error.TelegramError:  # Exception:  # as error:
        # logger.error(error, exc_info=True)
        logger.exception('Webhook update_queue FAILED')


def application_form(request):
    template_name = 'registration.html'
    context = {}  # values to pre-fill fields
    return render(request, template_name, context)