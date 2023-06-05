# Проект MSPP: 
[![MSPP CI/CD](https://github.com/alexpro2022/Telegram-Bot-for-MSPP/actions/workflows/main.yml/badge.svg)](https://github.com/alexpro2022/Telegram-Bot-for-MSPP/actions/workflows/main.yml)

Бот для «Московской школы профессиональной филантропии».
Позволяет НКО оперативно получать информацию о новых заявках в волонтёры в качестве наставников для детей-сирот.



## Оглавление:
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Создание и настройка аккаунта бота](#создание-и-настройка-аккаунта-бота)
- [Установка и запуск](#установка-и-запуск)
- [Активация бота](#активация-бота)
- [Удаление](#удаление)
- [Авторы](#авторы)



## Технологии:
<details><summary>Развернуть</summary>

**Языки программирования, библиотеки и модули:**

[![Python](https://img.shields.io/badge/Python-v3.11-blue?logo=python)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-v20.1-blue?)](https://docs.python-telegram-bot.org/en/stable/index.html)
[![asyncio](https://img.shields.io/badge/-asyncio-464646?logo=)](https://docs.python.org/3/library/asyncio.html)
[![environ](https://img.shields.io/badge/-environ-464646?logo=)](https://pypi.org/project/python-environ/)
[![inspect](https://img.shields.io/badge/-inspect-464646?logo=)](https://docs.python.org/3/library/inspect.html#the-interpreter-stack)
[![logging](https://img.shields.io/badge/-logging-464646?logo=)](https://docs.python.org/3/library/logging.html)
[![typing](https://img.shields.io/badge/-typing-464646?logo=)](https://docs.python.org/3/library/typing.html)
[![uvicorn](https://img.shields.io/badge/-uvicorn-464646?logo=Uvicorn)](https://www.uvicorn.org/)

[![JavaScript](https://img.shields.io/badge/-JavaScript-464646?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![HTML](https://img.shields.io/badge/-HTML-464646?logo=html)](https://html.spec.whatwg.org/multipage/)
[![CSS](https://img.shields.io/badge/-CSS-464646?logo=CSS)](https://developer.mozilla.org/ru/docs/Web/CSS)


**Фреймворк, расширения и библиотеки:**

[![Django](https://img.shields.io/badge/Django-v4.1-blue?logo=Django)](https://www.djangoproject.com/)
[![mptt](https://img.shields.io/badge/-mptt-464646?logo=django)](https://django-mptt.readthedocs.io/en/latest/)


**База данных:**

[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?logo=PostgreSQL)](https://www.postgresql.org/)


**CI/CD:**

[![GitHub_Actions](https://img.shields.io/badge/-GitHub_Actions-464646?logo=GitHub)](https://docs.github.com/en/actions)
[![docker_hub](https://img.shields.io/badge/-Docker_Hub-464646?logo=docker)](https://hub.docker.com/)
[![docker_compose](https://img.shields.io/badge/-Docker%20Compose-464646?logo=docker)](https://docs.docker.com/compose/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?logo=NGINX)](https://nginx.org/ru/)
[![SWAG](https://img.shields.io/badge/-SWAG-464646?logo=swag)](https://docs.linuxserver.io/general/swag)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?logo=Yandex)](https://cloud.yandex.ru/)
[![Telegram](https://img.shields.io/badge/-Telegram-464646?logo=Telegram)](https://core.telegram.org/api)


**Облачные технологии:**

[![Google](https://img.shields.io/badge/-Google_Cloud_Drive-464646?logo=google)](https://developers.google.com/drive)
[![Google](https://img.shields.io/badge/-Google_Cloud_Sheets-464646?logo=google)](https://developers.google.com/sheets)
[![Aiogoogle](https://img.shields.io/badge/-Aiogoogle-464646?logo=google)](https://aiogoogle.readthedocs.io/en/latest/)

[⬆️Оглавление](#оглавление)
</details>



## Описание работы:
Бот позволяет оформить онлайн-заявление:
  * в волонтёры-наставники для детей-сирот в фондах проекта **ЗНАЧИМ**
  * на включение местного фонда в проект **ЗНАЧИМ**

[⬆️Оглавление](#оглавление)



## Создание и настройка аккаунта бота:
<details><summary>Развернуть</summary>
1. @BotFather — регистрирует аккаунты ботов в Telegram:

Найдите в Telegram бота `@BotFather`: в окно поиска над списком контактов введите его имя.
Обратите внимание на иконку возле имени бота: белая галочка на голубом фоне. Эту иконку устанавливают администраторы Telegram, она означает, что бот настоящий, а не просто носит похожее имя. В любой непонятной ситуации выполняйте команду `/help` — и `@BotFather` покажет вам, на что он способен.

2. Создание аккаунта бота:

Начните диалог с ботом `@BotFather`: нажмите кнопку `Start` («Запустить»). Затем отправьте команду `/newbot` и укажите параметры нового бота:
   * имя (на любом языке), под которым ваш бот будет отображаться в списке контактов;
   * техническое имя вашего бота, по которому его можно будет найти в Telegram. Имя должно оканчиваться на слово bot в любом регистре. Имена ботов должны быть уникальны.

Аккаунт для вашего бота создан! 
`@BotFather` поздравит вас и отправит в чат токен для работы с Bot API. Токен выглядит примерно так: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`. По вашему запросу `@BotFather` может отозвать токен (отправьте боту `@BotFather` команду `/revoke`) и сгенерировать новый.

3. Настройка аккаунта бота:
Настроить аккаунт бота можно через `@BotFather`.
Отправьте команду `/mybots`; в ответ вы получите список ботов, которыми вы управляете (возможно, в этом списке лишь один бот). Укажите бота, которого хотите отредактировать, и нажмите кнопку `Edit Bot`.
Вы сможете изменить:
   * Имя бота (Edit Name).
   * Описание (Edit Description) — текст, который пользователи увидят в самом начале диалога с ботом под заголовком «Что может делать этот бот?»
   * Общую информацию (Edit About) — текст, который будет виден в профиле бота.
   * Картинку-аватар (Edit Botpic).
   * Команды (Edit Commands) — подсказки для ввода команд.

[⬆️Оглавление](#оглавление)
</details>



## Установка и запуск:
Удобно использовать принцип copy-paste - копировать команды из GitHub Readme и вставлять в командную строку Git Bash или IDE (например VSCode).
### Предварительные условия:
<details><summary>Развернуть</summary>

Предполагается, что пользователь:
  - создал [бота](#Создание-и-настройка-аккаунта-бота).
  - создал [сервисный аккаунт](https://support.google.com/a/answer/7378726?hl=en) на платформе Google Cloud и получил JSON-файл с информацией о своем сервисном аккаунте, его приватный ключ, ID и ссылки для авторизации. Эти данные будет необходимо указать в файле переменных окружения.
 - создал аккаунт [DockerHub](https://hub.docker.com/), если запуск будет производиться на удаленном сервере.
 - установил [Docker](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/) на локальной машине или на удаленном сервере, где проект будет запускаться в контейнерах. Проверить наличие можно выполнив команды:
    ```bash
    docker --version && docker-compose --version
    ```
</details>
<hr>
<details><summary>Локальный запуск</summary> 

**!!! Для пользователей Windows обязательно выполнить команду:** иначе файл start.sh при клонировании будет бракован:
```bash
git config --global core.autocrlf false
```

1. Установите [ngrok](https://ngrok.com/download).

2. Активируйте тоннель для https соединения командой:
```bash
ngrok http 80
``` 
В поле `Forwarding` первым элементом будет указано значение вида `https://ebd6-188-170-76-51.ngrok-free.app` - его потребуется указать в новом **.env**-файле в переменной окружения `DOMAIN` (можно как с протоколом `https://` , так и без него),  (см. п.4).

3. Не закрывайте окно терминала, иначе ngrok-тоннель также закроется. Откройте новое окно bash-терминала, в нем продолжим дальнейшую установку и запуск бота.

4. Клонируйте репозиторий с GitHub и в **.env**-файле введите данные для переменных окружения (значения даны для примера, но их можно оставить; подсказки даны в комментариях):
```bash
git clone https://github.com/alexpro2022/Telegram-Bot-for-MSPP.git && \
cd Telegram-Bot-for-MSPP && \
cp .env_example .env && \
nano .env
```
Для работы бота необходимо задать значения минимум трем переменным окружения: `TELEGRAM_BOT_TOKEN`, `DOMAIN`, `WEBHOOK_MODE`.
По умолчанию режим работы бота - `polling`. Этот режим удобен для первоначальной отладки бота, но в дальнейшем придется перейти на режим работы - `webhook`. Для этого задайте значение:
```bash
WEBHOOK_MODE=True
```

5. Запуск - из корневой директории проекта выполните команду:
```bash
docker compose -f infra/local/docker-compose.yml up -d --build
```
Проект будет развернут в трех docker-контейнерах (db, web, nginx) по адресу `http://localhost`.

6. Остановить docker и удалить контейнеры можно командой из корневой директории проекта:
```bash
docker compose -f infra/local/docker-compose.yml down
```
Если также необходимо удалить тома базы данных и статики:
```bash
docker compose -f infra/local/docker-compose.yml down -v
```
При повторных запусках приложения может потребоваться реактивация ngrok-тоннеля и обновление переменной окружения `DOMAIN` (см. п.2)
<hr></details>
<details><summary>Запуск на удаленном сервере</summary>

1. Создайте [домен](https://www.duckdns.org/domains) и привяжите его к публичному IP-адресу вашего удаленного сервера (введите его в поле current ip и кликните кнопку update ip).

2. Сделайте [форк](https://docs.github.com/en/get-started/quickstart/fork-a-repo) в свой репозиторий.

3. Создайте `Actions.Secrets` согласно списку ниже (значения указаны для примера) + переменные окружения из `env_example` файла:
```py
PROJECT_NAME=mspp-bot
SECRET_KEY

DOCKERHUB_USERNAME
DOCKERHUB_PASSWORD

# Данные удаленного сервера и ssh-подключения:
HOST  # публичный IP-адрес вашего удаленного сервера
USERNAME
SSH_KEY
PASSPHRASE
DOMAIN=mspp-bot.duckdns.org   # созданный домен

# Учетные данные Телеграм-бота для получения сообщения о успешном завершении workflow:
TELEGRAM_USER_ID
TELEGRAM_BOT_TOKEN

# База данных:
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_NAME=postgres
DB_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345
```

4. Запустите вручную `workflow`, чтобы автоматически развернуть проект в трех docker-контейнерах (db, web, nginx) на удаленном сервере.
</details>
<hr>

При первом запуске будут автоматически произведены следующие действия:    
  * выполнены миграции БД
  * БД заполнена начальными данными
  * создан суперюзер (пользователь с правами админа) с учетными данными из переменных окружения `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD`.
  * собрана статика

Вход в админ-зону осуществляется по адресу: http://`hostname`/admin/ , где `hostname`:
  * `localhost`
  * Доменное имя удаленного сервера, например `mspp-bot.duckdns.org`

[⬆️Оглавление](#оглавление)



## Активация бота:

Найдите своего бота по имени через поисковую строку — в окно поиска над списком контактов введите его имя. Напишите сообщение `/start`, чтобы активировать бота: теперь он сможет отправлять вам сообщения. Точно так же активировать вашего бота может любой, кто его найдёт.

[⬆️Оглавление](#оглавление)



## Удаление:
Для удаления проекта выполните команду:
```bash
cd .. && rm -fr Telegram-Bot-for-MSPP
```

[⬆️Оглавление](#оглавление)



## Авторы:

[Studio Yandex Practicum](https://github.com/Studio-Yandex-Practicum/mspp#%D0%B0%D0%B2%D1%82%D0%BE%D1%80%D1%8B)

[Aleksei Proskuriakov](https://github.com/alexpro2022)

- написал приложение registration для отображения форм регистрации нового наставника и нового фонда, использовал HTML, CSS для отображения форм в Telegram WebApp и JavaScript для real-time валидации полей форм.
- подключил doker-образ SWAG для получения SSL-сертификата (https соединение для webapp и webhook)
- переписал функционал обработчиков беседы бота и навигации (KISS, DRY, YAGNI)
- добавил дружественный интерфейс (эмоджи) и персонифицировал беседу (бот обрашается к пользователю по нику)
- реализовал вывод информации только для фондов, представленных в регионе/городе (а не всех фондов вообще)
- написал алгоритм меню для случая, если фонды одновременно могут быть и в регионе и в городах региона (хотя сама идея регионального фонда без привязки к населенному пункту выглядит спорно, но это в ТЗ)
- сделал пагинацию меню (меню регинов состоит из нескольких страниц по 5 регионов на каждой)
- реализовал отправку данных из форм в Google-таблицы после подверждения в меню confirmation из которого можно либо вернуться к повторному заполнению формы, если обнаружена некорректность в данных, либо отправить корректные данные в соответствующую таблицу (наставников или фондов).

[⬆️В начало](#Проект-MSPP)


