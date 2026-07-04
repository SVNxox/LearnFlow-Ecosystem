"""
LessonContent model — unified content item for a lesson.
"""

import uuid

from django.db import models
from django.db.models import Q

from .base import TimestampedModel


class LessonContent(TimestampedModel):
    """
    Unified content item for a lesson.

    One table handles all content types via a ``type`` discriminator.
    A lesson may have many content items displayed in order.

    type        url / body usage
    --------    -----------------------------------------------
    video       url = S3 key or external URL
    pdf         url = S3 key
    slides      url = S3 key or embed URL
    text        body = markdown
    link        url = external URL
    recording   url = S3 key
    code        body = source code

    metadata (JSONB) holds type-specific extras — see design doc for shape.
    """

    class Type(models.TextChoices):
        VIDEO = "video", "Video"
        PDF = "pdf", "PDF"
        SLIDES = "slides", "Slides"
        TEXT = "text", "Text"
        LINK = "link", "Link"
        RECORDING = "recording", "Recording"
        CODE = "code", "Code"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(
        "learning.Lesson", on_delete=models.CASCADE, related_name="contents", db_index=True
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.SmallIntegerField()
    url = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Used for video and recording. Shown in UI as '12 min'.",
    )
    file_size_bytes = models.BigIntegerField(
        null=True, blank=True, help_text="Used for pdf and downloadable files."
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Type-specific extras. Never queried via SQL — read at application level.",
    )
    is_required = models.BooleanField(
        default=True,
        help_text=(
            "If true, UserProgress domain must record this item as viewed "
            "before the lesson is considered complete."
        ),
    )
    is_downloadable = models.BooleanField(
        default=False,
        help_text="Meaningful for pdf, slides, recording. Controls download button.",
    )

    class Meta:
        db_table = "courses_lessoncontent"
        verbose_name = "Lesson Content"
        verbose_name_plural = "Lesson Contents"
        indexes = [
            models.Index(
                fields=["lesson_id", "order"],
                name="idx_content_lesson",
            ),
            
            models.Index(
                fields=["type", "lesson_id"],
                name="idx_content_type",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson_id", "order"],
                name="uq_content_lesson_order",
                deferrable=models.Deferrable.DEFERRED
            ),
            models.CheckConstraint(
                condition=Q(
                    type__in=["video", "pdf", "slides", "text", "link", "recording", "code"]
                ),
                name="chk_content_type",
            ),
            
            models.CheckConstraint(
                condition=Q(url__isnull=False) | Q(body__isnull=False),
                name="chk_content_has_source",
            ),
            models.CheckConstraint(
                condition=Q(order__gt=0),
                name="chk_content_order_positive",
            ),
            models.CheckConstraint(
                condition=Q(duration_seconds__isnull=True) | Q(duration_seconds__gt=0),
                name="chk_content_duration",
            ),
            models.CheckConstraint(
                condition=Q(file_size_bytes__isnull=True) | Q(file_size_bytes__gt=0),
                name="chk_content_file_size",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_type_display()}: {self.title}"
