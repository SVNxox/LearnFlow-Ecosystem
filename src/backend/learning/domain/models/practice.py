"""
LessonPractice model — in-platform practice exercise.
"""

import uuid

from django.db import models
from django.db.models import Q

from .base import TimestampedModel


class LessonPractice(TimestampedModel):
    """
    In-platform practice exercise — multiple per lesson, ordered.

    Unlike homework (submitted outside the platform), practice is done inline.
    The Assessment domain records student attempts, referencing LessonPractice.id
    read-only from this domain.
    """

    class Type(models.TextChoices):
        CODING = "coding", "Coding"
        WRITTEN = "written", "Written"
        INTERACTIVE = "interactive", "Interactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(
        "learning.Lesson", on_delete=models.CASCADE, related_name="practices", db_index=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.SmallIntegerField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.CODING)
    instructions = models.TextField()
    starter_code = models.TextField(
        null=True, blank=True, help_text="Pre-filled code shown to student. Type 'coding' only."
    )
    solution_code = models.TextField(
        null=True,
        blank=True,
        help_text="Reference solution. Never exposed to students. Type 'coding' only.",
    )
    language = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        help_text="Programming language for 'coding' type. e.g. 'python', 'javascript'.",
    )
    hints = models.JSONField(
        default=list,
        help_text="Ordered list of hint strings revealed progressively.",
    )
    max_score = models.SmallIntegerField(default=100)
    time_limit_minutes = models.SmallIntegerField(
        null=True, blank=True, help_text="Null = untimed."
    )

    class Meta:
        db_table = "courses_lessonpractice"
        verbose_name = "Lesson Practice"
        verbose_name_plural = "Lesson Practices"
        constraints = [
            models.UniqueConstraint(
                fields=["lesson_id", "order"],
                name="uq_practice_lesson_order",
            ),
            models.CheckConstraint(
                condition=Q(type__in=["coding", "written", "interactive"]),
                name="chk_practice_type",
            ),
            models.CheckConstraint(condition=Q(order__gt=0), name="chk_practice_order_positive"),
            models.CheckConstraint(condition=Q(max_score__gt=0), name="chk_practice_max_score"),
            models.CheckConstraint(
                condition=Q(time_limit_minutes__isnull=True) | Q(time_limit_minutes__gt=0),
                name="chk_practice_time_limit",
            ),
        ]

    def __str__(self) -> str:
        return self.title
