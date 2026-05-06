import os
import socket
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

_railway_public = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
if _railway_public:
    _railway_public = (
        _railway_public.removeprefix("https://").removeprefix("http://").split("/")[0].strip()
    )

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-in-production")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in ("1", "true", "yes")

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]
if _railway_public and _railway_public not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_public)

_on_railway = bool(
    os.getenv("RAILWAY_ENVIRONMENT")
    or os.getenv("RAILWAY_PROJECT_ID")
    or os.getenv("RAILWAY_SERVICE_ID")
)
_railway_host_suffix = ".up.railway.app"
if _on_railway and _railway_host_suffix not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_host_suffix)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "api",
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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

_database_url = os.getenv("DATABASE_URL", "").strip()

_sqlite_env = os.getenv("DJANGO_USE_SQLITE", "").strip().lower()
if _sqlite_env in ("0", "false", "no"):
    _use_sqlite = False
elif _sqlite_env in ("1", "true", "yes"):
    _use_sqlite = True
else:
    _use_sqlite = DEBUG

if _database_url:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(
            default=_database_url,
            conn_max_age=600,
            ssl_require=os.getenv("DATABASE_SSL_REQUIRE", "true").lower() in ("1", "true", "yes"),
        )
    }
elif _use_sqlite:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("MYSQL_DATABASE", "SIMConsultoria"),
            "USER": os.getenv("MYSQL_USER", "root"),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", ""),
            "HOST": os.getenv("MYSQL_HOST", "127.0.0.1"),
            "PORT": os.getenv("MYSQL_PORT", "3306"),
            "OPTIONS": {"charset": "utf8mb4"},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

_cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "").strip()
_cors_origin_regexes_raw = os.getenv("CORS_ALLOWED_ORIGIN_REGEXES", "").strip()

CORS_ALLOWED_ORIGINS = []
if _cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(",") if o.strip()]

_cors_regexes: list[str] = []
if _cors_origin_regexes_raw:
    _cors_regexes.extend(r.strip() for r in _cors_origin_regexes_raw.split(",") if r.strip())

if _on_railway and not DEBUG and not _cors_origins and not _cors_origin_regexes_raw:
    _cors_regexes.append(r"^https://[\w-]+\.netlify\.app$")

if _cors_regexes:
    CORS_ALLOWED_ORIGIN_REGEXES = _cors_regexes

if CORS_ALLOWED_ORIGINS or _cors_regexes:
    CORS_ALLOW_ALL_ORIGINS = False
else:
    CORS_ALLOW_ALL_ORIGINS = DEBUG

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

SIM_MARCA = os.getenv("SIM_MARCA", "SIM Consultoría")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "").strip()
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "").strip().replace(" ", "")
CONTACT_NOTIFY_EMAIL = os.getenv("CONTACT_NOTIFY_EMAIL", "").strip()
_explicit_email_backend = os.getenv("EMAIL_BACKEND", "").strip()
_has_smtp_creds = bool(EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)
_force_console = os.getenv("EMAIL_FORCE_CONSOLE", "").lower() in ("1", "true", "yes")

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "").strip()
EMAIL_USE_RESEND = bool(RESEND_API_KEY) and not _force_console

if _force_console:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
elif _has_smtp_creds:
    if _explicit_email_backend and "console" not in _explicit_email_backend.lower():
        EMAIL_BACKEND = _explicit_email_backend
    else:
        EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
elif _explicit_email_backend:
    EMAIL_BACKEND = _explicit_email_backend
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

_use_smtp = "smtp" in EMAIL_BACKEND.lower()
if _use_smtp:
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com").strip()
    _smtp_force_ipv4 = os.getenv("EMAIL_SMTP_FORCE_IPV4", "").lower() in ("1", "true", "yes")
    if _smtp_force_ipv4 and EMAIL_HOST:
        try:
            infos = socket.getaddrinfo(EMAIL_HOST, None, socket.AF_INET, socket.SOCK_STREAM)
            EMAIL_HOST = infos[0][4][0]
        except OSError:
            pass
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
    EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() in ("1", "true", "yes")
    EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "12"))
else:
    EMAIL_HOST = os.getenv("EMAIL_HOST", "")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_TIMEOUT = 10

_default_from = os.getenv("DEFAULT_FROM_EMAIL", "").strip()
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    DEFAULT_FROM_EMAIL = _default_from or f"SIM Consultoría <{EMAIL_HOST_USER}>"
else:
    DEFAULT_FROM_EMAIL = _default_from or "no-reply@localhost"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CSRF_TRUSTED_ORIGINS = []
for origin in (_cors_origins.split(",") if _cors_origins else []):
    o = origin.strip()
    if o.startswith("https://"):
        CSRF_TRUSTED_ORIGINS.append(o)
if _railway_public:
    _railway_origin = f"https://{_railway_public}"
    if _railway_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_railway_origin)
