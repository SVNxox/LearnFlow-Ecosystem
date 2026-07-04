"""
learnflow/settings/test.py

Test settings: SQLite database, simple password hasher, no Celery.
"""
from learnflow.settings.base import *  

import os

DEBUG = True
TEST_RUNNER = "django.test.runner.DiscoverRunner"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER = True


CORS_ALLOW_ALL_ORIGINS = True


SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
