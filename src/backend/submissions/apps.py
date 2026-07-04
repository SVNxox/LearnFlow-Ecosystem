"""
Submissions Domain — Django App Configuration
"""
from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.backend.submissions'
    label = 'submissions'
    verbose_name = 'Submissions Domain'

    def ready(self):
        """
        Register event handlers on app startup.
        """
        
        from src.backend.submissions.application import event_emitters  

        
        
        
        
