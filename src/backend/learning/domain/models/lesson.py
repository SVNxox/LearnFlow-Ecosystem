"""
Lesson model — atomic learning container.
"""

import uuid

from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel


class Lesson(SoftDeleteModel):
    """
    Atomic learning container.

    A lesson may contain:
      - zero or more LessonContent items
      - zero or one  LessonHomework
      - zero or more LessonPractice items
      - zero or one  LessonQuiz

    The lesson structure is identical for online and offline students.
    Delivery format lives on CourseEnrollment, not here.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        "learning.Module", on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.SmallIntegerField()
    is_published = models.BooleanField(default=False)
    is_free_preview = models.BooleanField(
        default=False,
        help_text="If true, lesson content is visible without enrollment (marketing).",
    )
    estimated_minutes = models.SmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "courses_lesson"
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        indexes = [
            
            models.Index(
                fields=["module_id", "order"],
                condition=Q(is_published=True, deleted_at__isnull=True),
                name="idx_lesson_module_published",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["module_id", "order"],
                condition=Q(deleted_at__isnull=True),
                name="uq_lesson_module_order",
            ),
            models.CheckConstraint(
                condition=Q(order__gt=0),
                name="chk_lesson_order_positive",
            ),
            models.CheckConstraint(
                condition=Q(estimated_minutes__isnull=True) | Q(estimated_minutes__gt=0),
                name="chk_lesson_estimated_minutes",
            ),
        ]

    def __str__(self) -> str:
        return self.title
