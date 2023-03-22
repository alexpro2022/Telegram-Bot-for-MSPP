# === WebAppInfo ========================================================================
async def get_new_application_form(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await update.callback_query.delete_message()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=s.PRESS_BUTTON_TO_FILL_FORM,
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                s.FILL_FORM_BUTTON_TEXT,
                # the TROUBLE below is local host isn't HTTPS - rejected by WebAppInfo
                # url (str) – An HTTPS URL of a Web App to be opened
                web_app=WebAppInfo(url="http://localhost")
                # below links are fully accesible as they are HTTPS:
                # (url="https://yandex.ru"),
                # (url="https://docs.python-telegram-bot.org/en/stable/examples.webappbot.html"),
            )
        ),
    )


# === URL ==============================================
from apps.bot.views import application_form

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bot/", include("bot.urls")),
    # preliminarily set in main urls.py - to be transferred to bot urls.py
    path("", application_form, name="application_form")
]    


# === View ================================================
def application_form(request):
    template_name = 'registration.html'
    context = {}  # values to pre-fill fields
    return render(request, template_name, context)


# ===Setting.py ===========================================

TEMPLATES = [
    {
        # ...
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        # ...

    }


# === PATH ================================================


```cmd
MSPP
|
|
+---src
|   |   
|   +---apps  
|   |
|   +---config  
|   |
|   +---templates  <-- директория для сохранения HTML-файлов
|   |                     registration.html
|   \---manage.py
|
+---infra
|
\---requirements


```


```html`

# === HTML =====================================
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Московская школа филантропии</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
  // To connect your Web App to the Telegram client, place the script telegram-web-app.js in the <head> tag before any other scripts, using this code:
  <script src="https://telegram.org/js/telegram-web-app.js"></script>


```  