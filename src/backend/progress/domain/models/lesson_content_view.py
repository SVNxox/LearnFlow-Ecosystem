"""
LessonContentView Model

Tracks which content items student has viewed.
Used for content gate calculation.

According to docs/DATABASE.md and docs/design/learnflow-userprogress-review-v2.md
"""
import uuid
from django.db import models
from django.utils import timezone


class LessonContentView(models.Model):
    """
    Records student views of lesson content items.

    One row per (enrollment, content) pair.
    Used to track content gate progress.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    enrollment_id = models.UUIDField(db_index=True)
    content_id = models.UUIDField()  
    lesson_progress_id = models.UUIDField(db_index=True)

    
    is_required = models.BooleanField()

    # Timestamps
    first_viewed_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(auto_now=True)

    # View tracking
    view_count = models.SmallIntegerField(default=1)

    # Video-specific tracking (F15 fix from review)
    last_position_seconds = models.IntegerField(null=True, blank=True)
    total_duration_seconds = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'progress_lessoncontentview'
        unique_together = [('enrollment_id', 'content_id')]
        indexes = [
            models.Index(fields=['enrollment_id', 'is_required']),
            models.Index(fields=['lesson_progress_id']),
        ]
        ordering = ['-last_viewed_at']

    def __str__(self):
        return f"LessonContentView(enrollment={self.enrollment_id}, content={self.content_id})"

    def watch_ratio(self) -> float:
        """
        Calculate watch ratio for videos (F15 fix).
        Returns 1.0 for non-video content.
        """
        if not self.total_duration_seconds or self.total_duration_seconds == 0:
            return 1.0

        if not self.last_position_seconds:
            return 0.0

        return min(self.last_position_seconds / self.total_duration_seconds, 1.0)
