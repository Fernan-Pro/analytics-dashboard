"""
Django settings for the Analytics Dashboard project.

Stack: Django 5.2 + DRF + PostgreSQL + Redis (cache / Celery broker).
Toda la configuración sensible se lee desde variables de entorno (.env).
"""

import os
import sys
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde backend/.env
load_dotenv(BASE_DIR / ".env")

# Hacer importables las apps modulares: apps/github, apps/reddit, ...
sys.path.insert(0, str(BASE_DIR / "apps"))

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-local-dev-only-change-me"
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "corsheaders",
    # Project apps (módulos)
    "analytics",
    "github",
    "hackernews",
    "producthunt",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Database (PostgreSQL por defecto; engine configurable vía env)
# En hosting tipo Render/PaaS se usa la variable DATABASE_URL (postgres://...)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DATABASE_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ.get("POSTGRES_DB", "analytics"),
        "USER": os.environ.get("POSTGRES_USER", "analytics_user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {"connect_timeout": 5},
    }
}

_database_url = os.environ.get("DATABASE_URL", "")
if _database_url:
    # Parsing manual del formato postgres://user:pass@host:port/name
    _url = _database_url.replace("postgres://", "", 1)
    if _url.startswith("postgresql://"):
        _url = _url.replace("postgresql://", "", 1)
    _creds, _rest = _url.split("@", 1) if "@" in _url else ("", _url)
    _user, _pass = _creds.split(":", 1) if ":" in _creds else (_creds, "")
    _host, _name = _rest.split("/", 1) if "/" in _rest else (_rest, "")
    _port = "5432"
    if ":" in _host:
        _host, _port = _host.rsplit(":", 1)
    DATABASES["default"].update(
        {
            "NAME": _name or DATABASES["default"]["NAME"],
            "USER": _user or DATABASES["default"]["USER"],
            "PASSWORD": _pass or DATABASES["default"]["PASSWORD"],
            "HOST": _host or DATABASES["default"]["HOST"],
            "PORT": _port or DATABASES["default"]["PORT"],
        }
    )

# ---------------------------------------------------------------------------
# Cache (Redis) - usado por Django Cache Framework y TanStack Query proxy
# ---------------------------------------------------------------------------
REDIS_URL = f"redis://{os.environ.get('REDIS_HOST', '127.0.0.1')}:{os.environ.get('REDIS_PORT', '6379')}/0"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", REDIS_URL),
        "TIMEOUT": 300,
    }
}

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "analytics.pagination.AnalyticsPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
}

# ---------------------------------------------------------------------------
# CORS (frontend Next.js en :3000)
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if o.strip()
]

# ---------------------------------------------------------------------------
# Logging: exponer requests y errores en stderr (clave para depurar en Render)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "formatters": {
        "simple": {
            "format": "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# ---------------------------------------------------------------------------
# API externas
# ---------------------------------------------------------------------------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
PRODUCT_HUNT_TOKEN = os.environ.get("PRODUCT_HUNT_TOKEN", "")

# Token del endpoint interno POST /api/admin/fetch/ (cron sin Redis).
# Vacío en local: el endpoint queda deshabilitado.
ADMIN_FETCH_TOKEN = os.environ.get("ADMIN_FETCH_TOKEN", "")

# ---------------------------------------------------------------------------
# Celery (broker Redis; configuración de beat en Fase 3)
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300

# ---------------------------------------------------------------------------
# Celery Beat - programación de tareas de scraping y agregación
# ---------------------------------------------------------------------------
CELERY_BEAT_SCHEDULE = {
    "fetch-github-trends-every-30min": {
        "task": "github.tasks.fetch_github_trends",
        "schedule": 30 * 60,
    },
    "fetch-hackernews-stories-every-15min": {
        "task": "hackernews.tasks.fetch_hackernews_stories",
        "schedule": 15 * 60,
    },
    "fetch-producthunt-launches-every-hour": {
        "task": "producthunt.tasks.fetch_producthunt_launches",
        "schedule": 60 * 60,
    },
    "aggregate-daily-metrics-at-0005": {
        "task": "analytics.tasks.aggregate_metrics",
        "schedule": crontab(hour=0, minute=5),
    },
}

# ---------------------------------------------------------------------------
# Seguridad / estáticos
# ---------------------------------------------------------------------------
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

LANGUAGE_CODE = "es-es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"