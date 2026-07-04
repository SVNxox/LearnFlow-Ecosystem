"""
Assignment Model

Unified model for homework, coding tasks, and project assignments.
Replaces LessonHomework + ProjectTask (ADR-014).
"""
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.utils import timezone


class Assignment(models.Model):
    """
    Assignment — описание задания.

    Типы:
    - theory: текстовые ответы на вопросы
    - coding: код-задачи (LeetCode-style)
    - project: полноценный проект

    Связи:
    - Lesson → Assignment (homework)
    - AssessmentItem → Assignment (project в assessment)
    """

    class AssignmentType(models.TextChoices):
        THEORY = 'theory', 'Theory'
        CODING = 'coding', 'Coding Task'
        PROJECT = 'project', 'Project'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    
    lesson_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Soft reference to learning.Lesson (SET NULL)"
    )

    assessment_item_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Soft reference to assessment.AssessmentItem"
    )

    type = models.CharField(
        max_length=20,
        choices=AssignmentType.choices
    )

    title = models.CharField(max_length=255)

    description = models.TextField(
        help_text="Markdown"
    )

    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    deadline_offset_days = models.SmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Days from enrollment date"
    )

    
    submission_types_allowed = ArrayField(
        models.CharField(max_length=30),
        default=list,
        help_text="['github_repository', 'file_upload', 'text_answer', 'external_link']"
    )

    allowed_file_extensions = models.CharField(
        max_length=200,
        blank=True,
        help_text=".pdf,.zip,.docx"
    )

    max_file_size_mb = models.SmallIntegerField(
        default=50,
        validators=[MinValueValidator(1)]
    )

    
    auto_check_enabled = models.BooleanField(
        default=False,
        help_text="Enable automatic checks (tests, linting, etc.)"
    )

    auto_check_config = models.JSONField(
        null=True,
        blank=True,
        help_text="Configuration for auto-checks"
    )

    created_by_id = models.UUIDField(
        db_index=True,
        help_text="Soft reference to accounts.User (staff)"
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'submissions_assignment'
        indexes = [
            models.Index(fields=['lesson_id'], name='idx_assign_lesson', condition=models.Q(lesson_id__isnull=False)),
            models.Index(fields=['assessment_item_id'], name='idx_assign_assess', condition=models.Q(assessment_item_id__isnull=False)),
            models.Index(fields=['type'], name='idx_assign_type'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type__in=['theory', 'coding', 'project']),
                name='chk_assign_type_valid'
            ),
            models.CheckConstraint(
                condition=models.Q(lesson_id__isnull=False) | models.Q(assessment_item_id__isnull=False),
                name='chk_assign_has_parent'
            ),
        ]

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"
