# === WebAppInfo ============================================================
async def register_user(
    update: Update,
    context: CallbackContext,
) -> None:
    """Инициализация формы регистрации пользователя."""
    query = None
    text = "Зарегистрироваться в проекте"
    if update.effective_message.web_app_data:
        query = urllib.parse.urlencode(json.loads(update.effective_message.web_app_data.data))
        text = "Исправить неверно внесенные данные"
    await update.message.reply_text(
        "Нажмите на кнопку ниже, чтобы перейти на форму регистрации.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.registration_template_url}?{query}"),
            )  # url (str) – An HTTPS URL of a Web App to be opened
        ),
    )


# === URL BUILDING ==========================================================    
    @property
    def registration_template_url(self) -> str:
        """Получить url-ссылку на HTML шаблон регистрации."""
        return urljoin(self.api_url, "telegram/registration_form")


    @property
    def api_url(self) -> str:
        return urljoin(self.APPLICATION_URL, self.ROOT_PATH)


# .env -----------------------------------------------------------------------
APPLICATION_URL= # домен, на котором развернуто приложение
#=============================================================================


# === ENDPOINT ================================================================
@router.get(
    "/registration_form",
    status_code=status.HTTP_200_OK,
    summary="Вернуть шаблон формы в телеграм",
    response_description="Предоставить пользователю форму для заполнения",
)
def user_register_form_webhook() -> StreamingResponse:
    """
    Вернуть пользователю в телеграм форму для заполнения персональных данных.
    """
    headers: dict[str, str] = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    def get_register_form() -> Iterator[bytes]:
        """
        Открывает для чтения html-шаблон формы регистрации пользователя.
        Возвращает генератор для последующего рендеринга шаблона StreamingResponse-ом.
        """
        with open(settings.registration_template, 'rb') as html_form:
            yield from html_form

    return StreamingResponse(get_register_form(), media_type="text/html", headers=headers)


# === TEMPLATE PATH ====================================================================
    @property
    def registration_template(self) -> Path:
        """Получить HTML-шаблон формы регистрации."""
        return BASE_DIR / "src" / "templates" / "registration" / "registration.html"
    

# === HTML =============================================   