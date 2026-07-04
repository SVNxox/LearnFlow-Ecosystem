"""
learnflow/settings/production.py

Production hardening: HTTPS headers, strict CORS, HSTS, whitenoise.
"""
from learnflow.settings.base import *  

import os

DEBUG = False


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["learnflow.uz", "www.learnflow.uz"])


CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[FRONTEND_URL])
CORS_ALLOW_CREDENTIALS = True





MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"




SECURE_SSL_REDIRECT              = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS              = 31536000   
SECURE_HSTS_INCLUDE_SUBDOMAINS   = True
SECURE_HSTS_PRELOAD              = True
SECURE_PROXY_SSL_HEADER          = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE            = True
CSRF_COOKIE_SECURE               = True
SECURE_REFERRER_POLICY           = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF      = True
X_FRAME_OPTIONS                  = "DENY"




DATABASES["default"]["CONN_MAX_AGE"] = 600  
DATABASES["default"]["OPTIONS"] = {  
    "connect_timeout": 10,
    "options": "-c statement_timeout=30000",  
}




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
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.request": {
            "level": "ERROR",
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




SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env("SENTRY_ENVIRONMENT", default="production"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
        send_default_pii=False,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
    )

print("🔒 LearnFlow PRODUCTION settings loaded")
