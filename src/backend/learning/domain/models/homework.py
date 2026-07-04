"""
LessonHomework model — assignment definition.
"""

import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q

from .base import TimestampedModel


class LessonHomework(TimestampedModel):
    """
    Assignment definition — at most one per lesson (OneToOne).

    This table defines *what* the student must submit.
    The submission itself (file upload, mentor review, scoring) lives in the
    Submissions domain, which reads these fields read-only.

    deadline_offset_days: relative, not absolute.
    Absolute deadline = lesson_unlocked_at + offset_days,
    computed by the Submissions domain at submission time.
    """

    class SubmissionType(models.TextChoices):
        FILE = "file", "File"
        LINK = "link", "Link"
        TEXT = "text", "Text"
        MIXED = "mixed", "Mixed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(
        "learning.Lesson", on_delete=models.CASCADE, related_name="homework"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(
        null=True,
        blank=True,
        help_text="Step-by-step guide, acceptance criteria, hints for where to start.",
    )
    max_score = models.SmallIntegerField(default=100)
    deadline_offset_days = models.SmallIntegerField(
        null=True,
        blank=True,
        help_text="Days after lesson unlock. Null = no deadline.",
    )
    submission_type = models.CharField(
        max_length=20,
        choices=SubmissionType.choices,
        default=SubmissionType.FILE,
    )
    allowed_file_types = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True,
        help_text="e.g. ['pdf', 'zip', 'docx']. Empty list = any type allowed.",
    )
    max_file_size_mb = models.SmallIntegerField(default=20)

    class Meta:
        db_table = "courses_lessonhomework"
        verbose_name = "Lesson Homework"
        verbose_name_plural = "Lesson Homeworks"
        constraints = [
            models.CheckConstraint(
                condition=Q(submission_type__in=["file", "link", "text", "mixed"]),
                name="chk_homework_submission_type",
            ),
            models.CheckConstraint(
                condition=Q(max_score__gt=0),
                name="chk_homework_max_score",
            ),
            models.CheckConstraint(
                condition=Q(deadline_offset_days__isnull=True) | Q(deadline_offset_days__gt=0),
                name="chk_homework_deadline_offset",
            ),
            models.CheckConstraint(
                condition=Q(max_file_size_mb__gt=0),
                name="chk_homework_file_size",
            ),
        ]

    def __str__(self) -> str:
        return self.title
