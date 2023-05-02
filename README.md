# Проект MSPP: 
Бот для «Московской школы профессиональной филантропии»
[![MSPP CI/CD](https://github.com/alexpro2022/Telegram-Bot-for-MSPP/actions/workflows/main.yml/badge.svg)](https://github.com/alexpro2022/Telegram-Bot-for-MSPP/actions/workflows/main.yml)



## Оглавление:
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Создание и настройка аккаунта бота](#Создание-и-настройка-аккаунта-бота)
- [Установка и запуск](#установка-и-запуск)
- [Активация бота](#активация-бота)
- [Автор](#автор)



## Технологии:


**Языки программирования, библиотеки и модули:**

[![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)](https://www.python.org/)

[![HTML](https://img.shields.io/badge/-HTML-464646?logo=html)](https://html.spec.whatwg.org/multipage/)
[![JavaScript](https://img.shields.io/badge/-JavaScript-464646?logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)


**Фреймворк, расширения и библиотеки:**

[![Django](https://img.shields.io/badge/-Django-464646?logo=Django)](https://www.djangoproject.com/)


**CI/CD:**

[![GitHub_Actions](https://img.shields.io/badge/-GitHub_Actions-464646?logo=GitHub)](https://docs.github.com/en/actions)
[![docker_hub](https://img.shields.io/badge/-Docker_Hub-464646?logo=docker)](https://hub.docker.com/)
[![docker_compose](https://img.shields.io/badge/-Docker%20Compose-464646?logo=docker)](https://docs.docker.com/compose/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?logo=NGINX)](https://nginx.org/ru/)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?logo=Yandex)](https://cloud.yandex.ru/)
[![Telegram](https://img.shields.io/badge/-Telegram-464646?logo=Telegram)](https://core.telegram.org/api)

[⬆️Оглавление](#оглавление)



## Описание работы:
Add your description here

[⬆️Оглавление](#оглавление)



## Создание и настройка аккаунта бота:
1. @BotFather — регистрирует аккаунты ботов в Telegram:

Найдите в Telegram бота @BotFather: в окно поиска над списком контактов введите его имя.
Обратите внимание на иконку возле имени бота: белая галочка на голубом фоне. Эту иконку устанавливают администраторы Telegram, она означает, что бот настоящий, а не просто носит похожее имя. В любой непонятной ситуации выполняйте команду /help — и @BotFather покажет вам, на что он способен.

2. Создание аккаунта бота:

Начните диалог с ботом @BotFather: нажмите кнопку Start («Запустить»). Затем отправьте команду /newbot и укажите параметры нового бота:
   * имя (на любом языке), под которым ваш бот будет отображаться в списке контактов;
   * техническое имя вашего бота, по которому его можно будет найти в Telegram. Имя должно оканчиваться на слово bot в любом регистре. Имена ботов должны быть уникальны.

Аккаунт для вашего бота создан! 
@BotFather поздравит вас и отправит в чат токен для работы с Bot API. Токен выглядит примерно так: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`. По вашему запросу @BotFather может отозвать токен (отправьте боту @BotFather команду /revoke) и сгенерировать новый.

3. Настройка аккаунта бота:
Настроить аккаунт бота можно через @BotFather.
Отправьте команду /mybots; в ответ вы получите список ботов, которыми вы управляете (возможно, в этом списке лишь один бот). Укажите бота, которого хотите отредактировать, и нажмите кнопку Edit Bot.
Вы сможете изменить:
   * Имя бота (Edit Name).
   * Описание (Edit Description) — текст, который пользователи увидят в самом начале диалога с ботом под заголовком «Что может делать этот бот?»
   * Общую информацию (Edit About) — текст, который будет виден в профиле бота.
   * Картинку-аватар (Edit Botpic).
   * Команды (Edit Commands) — подсказки для ввода команд.

[⬆️Оглавление](#оглавление)



## Установка и запуск:
Удобно использовать copy-paste - команды копировать из GitHub Readme и вставить в командную строку Git Bash или IDE (например VSCode).
### Предварительные условия:
Предполагается, что пользователь:
  - создал [бота](#Создание-и-настройка-аккаунта-бота)
  - создал [сервисный аккаунт](https://support.google.com/a/answer/7378726?hl=en) на платформе Google Cloud и получил JSON-файл с информацией о своем сервисном аккаунте, его приватный ключ, ID и ссылки для авторизации. Эти данные будет необходимо указать в файле переменных окружения.
  - установил [Docker](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/) на локальной машине или на удаленном сервере, где проект будет запускаться в контейнерах. Проверить наличие можно выполнив команды:
    ```
    docker --version && docker-compose --version
    ```
  - создал аккаунт [DockerHub](https://hub.docker.com/), если запуск будет производится на удаленном сервере.
<hr>
<details><summary>Локальный запуск: Docker Compose</summary> 

**!!! Для пользователей Windows обязательно выполнить команду:** иначе файл start.sh при клонировании будет бракован:
```
git config --global core.autocrlf false
```

1. Установите [ngrok](https://ngrok.com/download) и активируйте тоннель для https соединения. В поле Forwarding первым элементом будет указано значение вида `https://ebd6-188-170-76-51.ngrok-free.app`, которое необходимо указать в переменной окружения DOMAIN (можно как с протоколом https:// , так и без него) (см. п.2)

2. Клонируйте репозиторий с GitHub и в .env-файле введите данные для переменных окружения (значения даны для примера, но их можно оставить; подсказки даны в комментариях):
```
git clone git@github.com:alexpro2022/Telegram-Bot-for-MSPP.git && \
cd Telegram-Bot-for-MSPP && \
cp env_example .env && \
nano .env
```
Для работы бота необходимо задать значения минимум трем переменным окружения: TELEGRAM_BOT_TOKEN, DOMAIN, WEBHOOK_MODE.
По умолчанию режим работы бота - polling. Этот режим удобен для первоначальной отладки бота, но в дальнейшем придется перейти на режим работы - webhook. Для этого задайте значение:
```
WEBHOOK_MODE=True
```

3. Из корневой директории проекта выполните команду:
```
docker compose -f infra/local/docker-compose.yml up -d --build
```
Проект будет развернут в трех docker-контейнерах (db, web, nginx) по адресу http://localhost.

4. Остановить docker и удалить контейнеры можно командой из корневой директории проекта:
```
docker compose -f infra/local/docker-compose.yml down
```
Если также необходимо удалить тома базы данных, статики и медиа:
```
docker compose -f infra/local/docker-compose.yml down -v
```
</details></details>
<hr>
<details><summary>Запуск на удаленном сервере: Docker Compose</summary>

1. Создайте [домен](https://www.duckdns.org/domains) и привяжите его к публичному IP-адресу вашего удаленного сервера (введите его в поле current ip).

2. Сделайте [форк](https://docs.github.com/en/get-started/quickstart/fork-a-repo) в свой репозиторий.

3. Создайте Actions.Secrets согласно списку ниже (значения указаны для примера) + переменные окружения из env_example файла:
```
PROJECT_NAME=mspp-bot
SECRET_KEY

DOCKERHUB_USERNAME
DOCKERHUB_PASSWORD

# Данные удаленного сервера и ssh-подключения:
HOST  # публичный IP-адрес вашего удаленного сервера
USERNAME
SSH_KEY
PASSPHRASE
DOMAIN=mspp-bot.duckdns.org   

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

4. Запустите вручную workflow, чтобы автоматически развернуть проект в трех docker-контейнерах (db, web, nginx) на удаленном сервере.
</details>
<hr>

[⬆️Оглавление](#оглавление)



## Активация бота:

Найдите своего бота по имени через поисковую строку — в окно поиска над списком контактов введите его имя. Напишите сообщение `/start`, чтобы активировать его: теперь он сможет отправлять вам сообщения. Точно так же активировать вашего бота может любой, кто его найдёт.

[⬆️Оглавление](#оглавление)



## Автор:
[Aleksei Proskuriakov](https://github.com/alexpro2022)

[⬆️В начало](#Проект)


