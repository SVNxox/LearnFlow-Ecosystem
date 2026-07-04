from django.apps import AppConfig

class IdentityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.backend.identity'
    label = 'identity'

    def ready(self):
        try:
            from .extensions import CustomJWTAuthenticationExtension
        except ImportError:
            pass