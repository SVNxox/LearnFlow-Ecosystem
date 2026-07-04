"""
ModuleAssessment Model

Assessment attached to a module.
ADR-010: Assessment is a container, not a type.
The composition of items determines the "type" automatically.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class ModuleAssessment(models.Model):
    """
    Module Assessment — контейнер для assessment items.

    Тип определяется составом items автоматически:
    - Только single/multiple_choice = quiz
    - Только project = project assessment
    - Только interview = interview assessment
    - Смесь разных типов = mixed assessment
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    module_id = models.UUIDField(
        unique=True,
        db_index=True,
        help_text="Soft reference to learning.Module"
    )

    title = models.CharField(max_length=255)
    instructions = models.TextField(
        blank=True,
        help_text="Instructions shown to student before starting"
    )

    passing_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        default=Decimal('70.00'),
        help_text="Percentage required to pass (0-100)"
    )

    max_attempts = models.SmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="NULL = unlimited attempts"
    )

    time_limit_minutes = models.SmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="NULL = no time limit"
    )

    shuffle_items = models.BooleanField(
        default=False,
        help_text="Randomize item order for each attempt"
    )

    is_published = models.BooleanField(
        default=False,
        help_text="Only published assessments are visible to students"
    )

    created_by_id = models.UUIDField(
        db_index=True,
        help_text="Soft reference to accounts.User (staff)"
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assessment_moduleassessment'
        indexes = [
            models.Index(fields=['module_id'], name='idx_assess_module'),
            models.Index(fields=['is_published'], name='idx_assess_published'),
            models.Index(fields=['created_by_id'], name='idx_assess_creator'),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} (module {self.module_id})"

    @property
    def max_score(self) -> Decimal:
        """
        Calculate max score from all items.
        Cached at attempt creation time.
        """
        return self.items.aggregate(
            total=models.Sum('max_points')
        )['total'] or Decimal('0.00')
