"""
AssessmentAttempt Model

Student's attempt at taking an assessment.
Tracks grading status and final score.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class AssessmentAttempt(models.Model):
    """
    Assessment Attempt — попытка студента пройти assessment.

    Grading flow:
    1. Created → grading_status = pending
    2. Auto-graded items processed → auto_graded
    3. Mentor reviews manual items → mentor_review
    4. All items graded → finalized
    """

    class GradingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        AUTO_GRADED = 'auto_graded', 'Auto-Graded'
        MENTOR_REVIEW = 'mentor_review', 'Awaiting Mentor Review'
        FINALIZED = 'finalized', 'Finalized'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    enrollment_id = models.UUIDField(
        db_index=True,
        help_text="Soft reference to enrollment.CourseEnrollment"
    )

    assessment = models.ForeignKey(
        'assessment.ModuleAssessment',
        on_delete=models.PROTECT,
        related_name='attempts'
    )

    user_id = models.UUIDField(
        db_index=True,
        help_text="Denormalized from enrollment for quick queries"
    )

    attempt_number = models.SmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="1, 2, 3... (per enrollment)"
    )

    grading_status = models.CharField(
        max_length=20,
        choices=GradingStatus.choices,
        default=GradingStatus.PENDING,
        db_index=True
    )

    started_at = models.DateTimeField(
        default=timezone.now
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student submitted all responses"
    )

    graded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When grading_status became finalized"
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Set if time_limit_minutes configured"
    )

    max_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Snapshot of assessment.max_score"
    )

    final_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Sum of final_points from all responses"
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="final_score / max_score * 100"
    )

    passed = models.BooleanField(
        null=True,
        blank=True,
        help_text="percentage >= passing_percentage"
    )

    mentor_note = models.TextField(
        blank=True,
        help_text="General comment from mentor"
    )

    class Meta:
        db_table = 'assessment_assessmentattempt'
        indexes = [
            models.Index(fields=['enrollment_id', 'assessment'], name='idx_attempt_enr_assess'),
            models.Index(fields=['user_id', 'grading_status'], name='idx_attempt_user_status'),
            models.Index(fields=['grading_status'], name='idx_attempt_status'),
        ]
        ordering = ['-started_at']
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment_id', 'assessment', 'attempt_number'],
                name='uq_attempt_enr_assess_num'
            ),
            models.CheckConstraint(
                condition=models.Q(final_score__lte=models.F('max_score')),
                name='chk_attempt_score_valid'
            ),
        ]

    def __str__(self):
        return f"Attempt 

    def is_expired(self) -> bool:
        """Check if attempt has expired."""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def calculate_final_score(self):
        """
        Calculate final_score and percentage from responses.
        Called after all responses are graded.
        """
        from src.backend.assessment.domain.models import AssessmentResponse

        total = AssessmentResponse.objects.filter(
            attempt=self
        ).aggregate(
            total=models.Sum('final_points')
        )['total'] or Decimal('0.00')

        self.final_score = total
        if self.max_score > 0:
            self.percentage = (total / self.max_score) * 100
        else:
            self.percentage = Decimal('0.00')

        
        passing_pct = self.assessment.passing_percentage
        self.passed = self.percentage >= passing_pct

        self.save(update_fields=['final_score', 'percentage', 'passed'])
