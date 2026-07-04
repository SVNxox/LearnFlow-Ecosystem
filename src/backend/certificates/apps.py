"""
Certificates app configuration.
"""

from django.apps import AppConfig


class CertificatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.backend.certificates'
    label = 'certificates'
    verbose_name = 'Certificates Domain'

    def ready(self):
        """Import event handlers when app is ready."""
        try:
            import src.backend.certificates.application.handlers  
        except ImportError:
            pass
