"""
Django settings for updater_api project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
import tomllib
from datetime import datetime
from pathlib import Path

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.rq import RqIntegration

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
ENV_FILE = os.path.join(BASE_DIR, ".env")
LOG_DIR = os.path.join(BASE_DIR, "logs")
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
BUILD_FILE = Path(f"{BASE_DIR}/BUILD.txt")

# .env
if os.path.exists(ENV_FILE):
    load_dotenv(dotenv_path=ENV_FILE, verbose=True)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "dbs_tester")

if BUILD_FILE.exists():
    with open(BUILD_FILE) as f:
        BUILD = f.readline().replace("\n", "")
else:
    BUILD = datetime.now().isoformat()

with open(BASE_DIR / "pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)
    VERSION = pyproject["tool"]["poetry"]["version"]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django.forms",
    "django_rq",
    "django_bootstrap5",
    "admin_extra_buttons",
    "apps.core",
    "apps.web",
    "apps.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "dbs_tester.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.web.context_processors.info",
            ],
        },
    },
]

WSGI_APPLICATION = "dbs_tester.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": os.getenv("DATABASE_HOST"),
        "PORT": os.getenv("DATABASE_PORT", 5432),
        "NAME": os.getenv("DATABASE_NAME"),
        "USER": os.getenv("DATABASE_USER"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", None),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend", "apps.core.auth.LdapBackend"]

LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"

DATETIME_INPUT_FORMATS = ("%Y-%m-%dT%H:%M:%S%z",)

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 50  # 50MB

RQ_QUEUES = {
    "default": {
        "HOST": os.getenv("REDIS_HOST", "localhost"),
        "PORT": int(os.getenv("REDIS_PORT", 6379)),
        "DB": int(os.getenv("RQ_REDIS_DB", 0)),
        "PASSWORD": os.getenv("REDIS_PASSWORD", None),
        "DEFAULT_TIMEOUT": 360,
    }
}

RQ_EXCEPTION_HANDLERS = ["apps.core.jobs.exception_handler"]

RQ_SHOW_ADMIN_LINK = True

# Sentry
if os.getenv("SENTRY_DSN", False):

    def before_send(event, hint):
        if "exc_info" in hint:
            exc_type, exc_value, tb = hint["exc_info"]
            if exc_type.__name__ in ["ValidationException"]:
                return None
        if "extra" in event and not event["extra"].get("to_sentry", True):
            return None

        return event

    sentry_sdk.init(
        integrations=[RedisIntegration(), RqIntegration(), DjangoIntegration()],
        attach_stacktrace=True,
        send_default_pii=True,
        request_bodies="always",
        before_send=before_send,
        release=VERSION,
    )

CRON_JOBS = {"prune": "*/5 * * * *"}

PAGINATION_DEFAULT_LIMIT = 10

DBS_TESTER_TIMEOUT = 20
DBS_DATABASES_PATH = os.getenv("DBS_DATABASES_PATH", "/var/databases")
DBS_TESTER_DIFF_THRESHOLD = 1024 * 512
DBS_DOCKER_NETWORK = os.getenv("DBS_DOCKER_NETWORK", "dbs")

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

PG_RESTORE_PATH = os.getenv("PG_RESTORE_PATH", "/usr/bin/pg_restore")
