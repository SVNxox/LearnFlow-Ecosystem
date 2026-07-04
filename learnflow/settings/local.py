"""
learnflow/settings/local.py

Settings for LOCAL development (without Docker).
Use this when running Django directly on your machine.

Usage:
    export DJANGO_SETTINGS_MODULE=learnflow.settings.local
    python manage.py runserver
"""
from learnflow.settings.base import *  

DEBUG = True
ALLOWED_HOSTS = ["*"]





DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", default="learnflow_local"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
        "ATOMIC_REQUESTS": False,
        "CONN_MAX_AGE": 60,
    }
}





REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "lf_local",
    }
}





CELERY_BROKER_URL = env("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default=REDIS_URL)





EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@learnflow.local")






AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID", default="minioadmin")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY", default="minioadmin")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="learnflow-local")
AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL", default="http://localhost:9000")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")





CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True





try:
    import debug_toolbar  
    INSTALLED_APPS += ["debug_toolbar"]  
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
except ImportError:
    pass





LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.db.backends": {
            "level": "INFO",  
            "handlers": ["console"],
            "propagate": False,
        },
        "src.backend.identity": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "src.backend.learning": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "celery": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}






PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",  
]


MAX_FAILED_ATTEMPTS = 3  
LOCKOUT_MINUTES = 5  

print("=" * 80)
print("🚀 LearnFlow LOCAL settings loaded")
print("=" * 80)
print(f"📊 Database: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}")
print(f"📮 Redis: {REDIS_URL}")
print(f"📧 Email: Console (printed to terminal)")
print(f"🗄️  S3: {AWS_S3_ENDPOINT_URL}")
print(f"🌐 CORS: {', '.join(CORS_ALLOWED_ORIGINS)}")
print(f"🐛 Debug: {DEBUG}")
print("=" * 80)
