"""
Enrollment Domain Django App Configuration.
"""

from django.apps import AppConfig


class EnrollmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.backend.enrollment'
    label = 'enrollment'
    verbose_name = 'Enrollment Domain'
