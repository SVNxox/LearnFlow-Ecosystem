"""
Managers for learning app.

SoftDeleteManager excludes deleted rows by default.
"""

from django.db import models


class SoftDeleteManager(models.Manager):
    """
    Manager that automatically excludes soft-deleted rows.

    Usage:
        class MyModel(models.Model):
            deleted_at = models.DateTimeField(null=True, blank=True)

            objects = SoftDeleteManager()  
            all_objects = models.Manager()  
    """

    def get_queryset(self):
        """Return queryset excluding soft-deleted rows (deleted_at IS NULL)."""
        return super().get_queryset().filter(deleted_at__isnull=True)
