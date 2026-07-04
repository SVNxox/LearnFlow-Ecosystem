"""
learnflow/settings/development.py

Development overrides: debug toolbar, console email, relaxed CORS.
"""
from learnflow.settings.base import *  

DEBUG = True
ALLOWED_HOSTS = ["*"]







try:
    import debug_toolbar  
    INSTALLED_APPS += ["debug_toolbar"]  
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass


CORS_ALLOW_ALL_ORIGINS = True





