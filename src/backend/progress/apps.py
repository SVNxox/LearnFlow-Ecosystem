"""
UserProgress Domain App Configuration
"""
from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.backend.progress'
    label = 'progress'
    verbose_name = 'User Progress'

    def ready(self):
        """
        Import signal handlers when Django starts.
        """
        try:
            from .application.handlers import event_handlers  
        except ImportError:
            pass
