"""
AssessmentReviewLog Model

Audit trail for mentor score overrides.
ADR-011: All score changes must be logged with reason.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class AssessmentReviewLog(models.Model):
    """
    Assessment Review Log — история изменений оценок ментором.

    Зачем: Споры студент/ментор через год.
    История покажет кто, когда и почему изменил балл.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    response = models.ForeignKey(
        'assessment.AssessmentResponse',
        on_delete=models.CASCADE,
        related_name='review_logs'
    )

    attempt_id = models.UUIDField(
        db_index=True,
        help_text="Denormalized for quick queries"
    )

    old_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Score before change"
    )

    new_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Score after change"
    )

    mentor_id = models.UUIDField(
        db_index=True,
        help_text="Soft reference to accounts.User (mentor)"
    )

    reason = models.TextField(
        help_text="Why the score was changed (required)"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )

    class Meta:
        db_table = 'assessment_assessmentreviewlog'
        indexes = [
            models.Index(fields=['response'], name='idx_revlog_response'),
            models.Index(fields=['attempt_id'], name='idx_revlog_attempt'),
            models.Index(fields=['mentor_id'], name='idx_revlog_mentor'),
            models.Index(fields=['-created_at'], name='idx_revlog_created'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by mentor {self.mentor_id}: {self.old_score} → {self.new_score}"
