"""
SubmissionFile Model

Files uploaded by student (for type=file_upload).
Includes virus scanning status.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class SubmissionFile(models.Model):
    """
    Submission File — файл загруженный студентом.

    Security:
    - Virus scanning (ClamAV) обязателен
    - MIME type validation
    - File size limits
    - Archive bomb protection
    """

    class ScanStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        PASSED = 'passed', 'Passed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    revision = models.ForeignKey(
        'submissions.SubmissionRevision',
        on_delete=models.CASCADE,
        related_name='files'
    )

    file_name = models.CharField(max_length=255)

    file_size_bytes = models.BigIntegerField(
        validators=[MinValueValidator(1)]
    )

    mime_type = models.CharField(
        max_length=100,
        help_text="Validated from file content, not extension"
    )

    storage_path = models.TextField(
        help_text="S3 path: submissions/{revision_id}/{file_id}"
    )

    
    scan_status = models.CharField(
        max_length=20,
        choices=ScanStatus.choices,
        default=ScanStatus.PENDING,
        db_index=True
    )

    scan_result = models.JSONField(
        null=True,
        blank=True,
        help_text="ClamAV scan results"
    )

    scanned_at = models.DateTimeField(
        null=True,
        blank=True
    )

    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'submissions_submissionfile'
        indexes = [
            models.Index(fields=['revision'], name='idx_file_revision'),
            models.Index(
                fields=['scan_status', 'uploaded_at'],
                name='idx_file_scan_pending',
                condition=models.Q(scan_status__in=['pending', 'running'])
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(scan_status__in=['pending', 'running', 'passed', 'failed']),
                name='chk_file_scan_valid'
            ),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.scan_status})"

    def is_safe(self) -> bool:
        """Check if file passed virus scan."""
        return self.scan_status == self.ScanStatus.PASSED
