"""
SubmissionReview Model

Mentor review of a submission revision.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class SubmissionReview(models.Model):
    """
    Submission Review — проверка ментора.

    Один review на одну revision.
    Ментор проверяет конкретную версию, не submission целиком.
    """

    class ReviewStatus(models.TextChoices):
        CHANGES_REQUESTED = 'changes_requested', 'Changes Requested'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    submission = models.ForeignKey(
        'submissions.Submission',
        on_delete=models.PROTECT,
        related_name='reviews'
    )

    revision = models.ForeignKey(
        'submissions.SubmissionRevision',
        on_delete=models.PROTECT,
        related_name='reviews'
    )

    mentor_id = models.UUIDField(
        db_index=True,
        help_text="Soft reference to accounts.User (mentor)"
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Snapshot from assignment"
    )

    feedback = models.TextField(
        help_text="Mentor's feedback"
    )

    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices
    )

    reviewed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'submissions_submissionreview'
        indexes = [
            models.Index(fields=['submission'], name='idx_review_submission'),
            models.Index(fields=['revision'], name='idx_review_revision'),
            models.Index(fields=['mentor_id'], name='idx_review_mentor'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['submission', 'revision'],
                name='uq_review_subm_rev'
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=['changes_requested', 'approved', 'rejected']),
                name='chk_review_status_valid'
            ),
            models.CheckConstraint(
                condition=models.Q(score__lte=models.F('max_score')),
                name='chk_review_score_valid'
            ),
        ]

    def __str__(self):
        return f"Review by mentor {self.mentor_id}: {self.status}"
