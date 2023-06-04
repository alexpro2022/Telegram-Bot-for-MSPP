import logging
import sys
from pathlib import Path
from urllib.parse import urljoin

import environ
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "apps"))

env = environ.Env()

SECRET_KEY = env("SECRET_KEY", default=get_random_secret_key())

DEBUG = env.bool("DEBUG", default=True)

PROTO = "https://"
DOMAIN = env("DOMAIN").replace(PROTO, "")
ALLOWED_HOSTS = [DOMAIN, 'localhost']
APPLICATION_URL = f"{PROTO}{DOMAIN}"
CSRF_TRUSTED_ORIGINS = [APPLICATION_URL]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mptt",
    "registration",
    "bot.apps.BotConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="mspp"),
        "USER": env("POSTGRES_USER", default="mspp"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="pg_password"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Telegram
TELEGRAM_TOKEN = env("TELEGRAM_BOT_TOKEN", default="")
WEBHOOK_MODE = env.bool("WEBHOOK_MODE", default=False)
WEBHOOK_URL = urljoin(APPLICATION_URL, "bot/")

# Google
# SPREADSHEETS_URL = "https://docs.google.com/spreadsheets/d/{0}"
FUNDS_SPREADSHEET_ID = env("FUNDS_SPREADSHEET_ID", default="_")
MENTORS_SPREADSHEET_ID = env("MENTORS_SPREADSHEET_ID", default="_")

ENV_INFO = {
    "project_id": env("PROJECT_ID", default="_"),
    "private_key_id": env("PRIVATE_KEY_ID", default="_"),
    "private_key": env.str("PRIVATE_KEY", multiline=True, default="_"),
    "client_email": env("CLIENT_EMAIL", default="_"),
    "client_id": env("CLIENT_ID", default="_"),
    "client_x509_cert_url": env("CLIENT_X509_CERT_URL", default="_"),
}

TYPE = "Service_account"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
AUTH_PROVIDER_X509_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
SCOPES = ("https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive")
INFO = {
    "type": TYPE,
    "auth_uri": AUTH_URI,
    "token_uri": TOKEN_URI,
    "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL,
    "scopes": SCOPES,
    **ENV_INFO,
}

LOGGING_LEVEL = env("LOGGING_LEVEL", default="INFO")
LOG_DIR = BASE_DIR / "logs"
LOGGING_FILENAME = LOG_DIR / "main.log"
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGGING_FILENAME, encoding='utf-8'),
    ]
)

EMOJI = env("EMOJI", default=True)
EMAIL = env("EMAIL", default="example@mail.com")

MENU_ITEMS_PER_PAGE = 5
