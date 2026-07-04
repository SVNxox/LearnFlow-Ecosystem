"""
Submission Model

Container for student's attempt to complete an assignment.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Submission(models.Model):
    """
    Submission — попытка студента выполнить задание.

    Контейнер для ревизий (версий).
    Один студент = одна submission на assignment.
    """

    class SubmissionStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        UNDER_REVIEW = 'under_review', 'Under Review'
        CHANGES_REQUESTED = 'changes_requested', 'Changes Requested'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    assignment = models.ForeignKey(
        'submissions.Assignment',
        on_delete=models.PROTECT,
        related_name='submissions'
    )

    enrollment_id = models.UUIDField(
        db_index=True,
        help_text="Soft reference to enrollment.CourseEnrollment"
    )

    student_id = models.UUIDField(
        db_index=True,
        help_text="Denormalized for quick queries"
    )

    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.DRAFT,
        db_index=True
    )

    current_revision_number = models.SmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    final_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Final score after approval"
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    first_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When first submitted for review"
    )

    last_submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When last submitted for review"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When approved or rejected"
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Calculated from assignment.deadline_offset_days"
    )

    class Meta:
        db_table = 'submissions_submission'
        indexes = [
            models.Index(fields=['enrollment_id', 'assignment'], name='idx_subm_enr_assign'),
            models.Index(fields=['student_id', 'status'], name='idx_subm_student_status'),
            models.Index(fields=['status'], name='idx_subm_status'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment_id', 'assignment'],
                name='uq_subm_enr_assign'
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    'draft', 'submitted', 'under_review',
                    'changes_requested', 'approved', 'rejected'
                ]),
                name='chk_subm_status_valid'
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission by student {self.student_id} for {self.assignment.title}"

    def is_overdue(self) -> bool:
        """Check if submission is past deadline."""
        if not self.deadline:
            return False
        return timezone.now() > self.deadline
