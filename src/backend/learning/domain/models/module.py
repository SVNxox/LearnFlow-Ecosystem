"""
Module model — ordered grouping of Lessons within a Course.
"""

import uuid

from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel


class Module(SoftDeleteModel):
    """
    Ordered grouping of Lessons within a Course.

    Assessment granularity: end-of-module exams live in the Assessment domain
    and reference Module.id.  This table never writes to that domain.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "learning.Course", on_delete=models.CASCADE, related_name="modules"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.SmallIntegerField()
    is_published = models.BooleanField(default=False)
    estimated_hours = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "courses_module"
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        indexes = [
            
            models.Index(
                fields=["course_id", "order"],
                condition=Q(is_published=True, deleted_at__isnull=True),
                name="idx_module_course_published",
            ),
        ]
        constraints = [
            
            models.UniqueConstraint(
                fields=["course_id", "order"],
                condition=Q(deleted_at__isnull=True),
                name="uq_module_course_order",
            ),
            models.CheckConstraint(
                condition=Q(order__gt=0),
                name="chk_module_order_positive",
            ),
            models.CheckConstraint(
                condition=Q(estimated_hours__isnull=True) | Q(estimated_hours__gt=0),
                name="chk_module_estimated_hours",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.course} — {self.title}"
