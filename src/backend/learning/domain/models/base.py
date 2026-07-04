"""
Base abstract models for Learning Domain.

These provide common timestamp and soft-delete patterns.
"""

from django.db import models
from django.utils import timezone

from src.backend.learning.managers import SoftDeleteManager


class TimestampedModel(models.Model):
    """Mixin: created_at + updated_at (auto-managed)."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimestampedModel):
    """
    Mixin: logical deletion via ``deleted_at`` timestamp.

    ``Model.objects``      → excludes deleted rows  (SoftDeleteManager)
    ``Model.all_objects``  → all rows including deleted  (plain Manager)
    """

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    
    
    

    def delete(self, using=None, keep_parents=False):  
        """Soft-delete: stamp deleted_at, keep the row."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently remove the row from the database."""
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Undo a soft-delete."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    class Meta:
        abstract = True
