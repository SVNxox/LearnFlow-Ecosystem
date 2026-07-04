"""
AssessmentResponse Model

Student's response to a single assessment item.
ADR-011: Supports mentor override with audit trail.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone


class AssessmentResponse(models.Model):
    """
    Assessment Response — ответ студента на один item.

    Scoring:
    - auto_points: автоматическая оценка (choice, coding)
    - mentor_points: ментор может пересмотреть (override)
    - final_points: COALESCE(mentor_points, auto_points)
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    attempt = models.ForeignKey(
        'assessment.AssessmentAttempt',
        on_delete=models.CASCADE,
        related_name='responses'
    )

    item = models.ForeignKey(
        'assessment.AssessmentItem',
        on_delete=models.PROTECT,
        related_name='responses'
    )

    selected_option_ids = ArrayField(
        models.UUIDField(),
        default=list,
        blank=True,
        help_text="For single_choice and multiple_choice"
    )

    text_response = models.TextField(
        blank=True,
        help_text="For text_answer and interview"
    )

    submitted_code = models.TextField(
        blank=True,
        help_text="For coding type"
    )

    coding_language = models.CharField(
        max_length=30,
        blank=True,
        help_text="Language used for coding submission"
    )

    submission_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Soft reference to submissions.ProjectSubmission (for project type)"
    )

    is_graded = models.BooleanField(
        default=False,
        db_index=True
    )

    auto_points = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Auto-grading result"
    )

    mentor_points = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Mentor override (takes precedence)"
    )

    final_points = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="COALESCE(mentor_points, auto_points)"
    )

    is_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="For choice items (binary correct/incorrect)"
    )

    reviewed_by_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Soft reference to accounts.User (mentor)"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    review_comment = models.TextField(
        blank=True,
        help_text="Mentor's feedback or reason for override"
    )

    class Meta:
        db_table = 'assessment_assessmentresponse'
        indexes = [
            models.Index(fields=['attempt', 'item'], name='idx_resp_attempt_item'),
            models.Index(fields=['is_graded'], name='idx_resp_graded'),
            models.Index(fields=['reviewed_by_id'], name='idx_resp_reviewer'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['attempt', 'item'],
                name='uq_resp_attempt_item'
            ),
        ]

    def __str__(self):
        return f"Response to item {self.item.order} (attempt {self.attempt.id})"

    def save(self, *args, **kwargs):
        """Auto-calculate final_points."""
        self.final_points = self.mentor_points if self.mentor_points is not None else self.auto_points
        super().save(*args, **kwargs)

    def apply_mentor_override(self, mentor_id: str, new_score: Decimal, reason: str):
        """
        Apply mentor override and log to ReviewLog.
        ADR-011: Audit trail for all score changes.
        """
        from src.backend.assessment.domain.models import AssessmentReviewLog

        old_score = self.final_points or Decimal('0.00')

        self.mentor_points = new_score
        self.final_points = new_score
        self.reviewed_by_id = mentor_id
        self.reviewed_at = timezone.now()
        self.review_comment = reason
        self.is_graded = True
        self.save()

        AssessmentReviewLog.objects.create(
            response=self,
            attempt_id=self.attempt_id,
            old_score=old_score,
            new_score=new_score,
            mentor_id=mentor_id,
            reason=reason
        )
