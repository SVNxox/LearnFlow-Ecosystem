"""
Mentorship app configuration.
"""

from django.apps import AppConfig


class MentorshipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.backend.mentorship'
    label = 'mentorship'
    verbose_name = 'Mentorship Domain'

    def ready(self):
        """Import event handlers when app is ready."""
        try:
            import src.backend.mentorship.application.handlers  
        except ImportError:
            pass
