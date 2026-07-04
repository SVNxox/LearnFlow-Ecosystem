"""
AutoCheck Model

Automatic checks (tests, linting, coverage, etc.).
Separate from mentor review.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class AutoCheck(models.Model):
    """
    Auto Check — автоматическая проверка submission.

    Types:
    - tests: unit/integration tests
    - linting: code style (black, flake8, eslint)
    - coverage: test coverage percentage
    - docker_build: Docker image build
    - security: security scan (bandit, safety)
    """

    class CheckStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        PASSED = 'passed', 'Passed'
        FAILED = 'failed', 'Failed'
        ERROR = 'error', 'Error'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    revision = models.ForeignKey(
        'submissions.SubmissionRevision',
        on_delete=models.CASCADE,
        related_name='auto_checks'
    )

    check_type = models.CharField(
        max_length=30,
        help_text="tests, linting, coverage, docker_build, security"
    )

    status = models.CharField(
        max_length=20,
        choices=CheckStatus.choices,
        default=CheckStatus.PENDING,
        db_index=True
    )

    score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Score if applicable"
    )

    report = models.JSONField(
        help_text="Detailed check results"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'submissions_autocheck'
        indexes = [
            models.Index(fields=['revision', 'check_type'], name='idx_check_rev_type'),
            models.Index(fields=['status'], name='idx_check_status'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['pending', 'running', 'passed', 'failed', 'error']),
                name='chk_check_status_valid'
            ),
        ]

    def __str__(self):
        return f"{self.check_type}: {self.status}"
