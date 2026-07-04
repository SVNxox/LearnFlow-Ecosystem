"""
learnflow/settings/base.py

Base settings shared across all environments.
Environment-specific overrides live in development.py and production.py.
"""
import os
from datetime import timedelta
from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()

environ.Env.read_env(env_file=str(BASE_DIR / ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

TELEGRAM_BOT_TOKEN = env('TELEGRAM_BOT_TOKEN')
TELEGRAM_BOT_USERNAME = env('TELEGRAM_BOT_USERNAME')
CLICK_PROVIDER_TOKEN = env('CLICK_PROVIDER_TOKEN')

FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",

    
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",

    
    "src.backend.identity",
    "src.backend.learning",
    "src.backend.enrollment",
    "src.backend.payment",
    "src.backend.progress",
    "src.backend.assessment",
    "src.backend.submissions",
    "src.backend.certificates",
    "src.backend.mentorship",
    "src.backend.notifications",
    "src.backend.audit",
    "src.backend.telegram_bot",
    "src.backend.core",
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
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = "learnflow.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS":    [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "learnflow.wsgi.application"


DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://learnflow:learnflow@localhost:5432/learnflow")
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False  


AUTH_USER_MODEL = "identity.User"  

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


JWT_PRIVATE_KEY = env("JWT_PRIVATE_KEY", default="").replace("\\n", "\n") or None
JWT_PUBLIC_KEY  = env("JWT_PUBLIC_KEY",  default="").replace("\\n", "\n") or None


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "src.backend.identity.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'EXCEPTION_HANDLER': 'src.backend.core.exception_handler.custom_exception_handler',
}


SPECTACULAR_SETTINGS = {
    "TITLE":       "LearnFlow API",
    "DESCRIPTION": "Online learning platform — REST API documentation",
    "VERSION":     "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,

    
    "SECURITY": [{"BearerAuth": []}],

    "SECURITY_SCHEMES": {
        "BearerAuth": {
            "type":   "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    },

    
    "AUTHENTICATION_WHITELIST": [
        "src.backend.identity.authentication.JWTAuthentication",
    ],

    
    "AUTHENTICATION_CLASSES": [
        "src.backend.identity.authentication.JWTAuthentication",
    ],

    
    "ENUM_GENERATE_CHOICE_DESCRIPTION": True,

    
    "TAGS": [
        {"name": "Identity — Auth",             "description": "Authentication & registration"},
        {"name": "Identity — Email Verification", "description": "Email confirmation flow"},
        {"name": "Identity — Password Reset",   "description": "Password reset flow"},
        {"name": "Identity — Profile",          "description": "User profile management"},
        {"name": "Identity — Settings",         "description": "User preferences"},
        {"name": "Identity — Sessions",         "description": "Active session management"},
    ],

    
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "COMPONENT_SPLIT_REQUEST": True,

    
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],

    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        
        "showExtensions": True,
    },
}


REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND":  "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "lf",
    }
}


CELERY_BROKER_URL        = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND    = env("CELERY_RESULT_BACKEND", default=REDIS_URL)
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE          = "UTC"
CELERY_BEAT_SCHEDULER    = "django_celery_beat.schedulers:DatabaseScheduler"

CELERY_TASK_ROUTES = {
    "src.backend.identity.tasks.*":      {"queue": "email"},
    "src.backend.notifications.tasks.*": {"queue": "notifications"},
}


DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@learnflow.uz")
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")


CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://localhost:5173"],
)
CORS_ALLOW_CREDENTIALS = True


AWS_ACCESS_KEY_ID       = env("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY   = env("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="learnflow")
AWS_S3_ENDPOINT_URL     = env("AWS_S3_ENDPOINT_URL", default="")
AWS_S3_REGION_NAME      = env("AWS_S3_REGION_NAME", default="us-east-1")


STATIC_URL  = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL   = "/media/"
MEDIA_ROOT  = BASE_DIR / "media"


LANGUAGE_CODE = "uz"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True
LANGUAGES = [('uz', 'Uzbek'), ('ru', 'Russian'), ('en', 'English')]


X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level":    "INFO",
    },
    "loggers": {
        "django.db.backends": {
            "level":     "WARNING",
            "handlers":  ["console"],
            "propagate": False,
        },
        "src.backend.identity": {
            "level":     "INFO",
            "handlers":  ["console"],
            "propagate": False,
        },
    },
}
