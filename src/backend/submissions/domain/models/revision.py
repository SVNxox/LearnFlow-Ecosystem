"""
SubmissionRevision Model

Versions of submission (student resubmits after feedback).
ADR-016: Versioning is mandatory.
"""
import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class SubmissionRevision(models.Model):
    """
    Submission Revision — версия submission.

    Студент почти всегда пересдаёт работу после замечаний.
    Каждая пересдача = новая revision.
    """

    class SubmissionType(models.TextChoices):
        GITHUB_REPOSITORY = 'github_repository', 'GitHub Repository'
        FILE_UPLOAD = 'file_upload', 'File Upload'
        TEXT_ANSWER = 'text_answer', 'Text Answer'
        EXTERNAL_LINK = 'external_link', 'External Link'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    submission = models.ForeignKey(
        'submissions.Submission',
        on_delete=models.CASCADE,
        related_name='revisions'
    )

    revision_number = models.SmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="1, 2, 3..."
    )

    submission_type = models.CharField(
        max_length=20,
        choices=SubmissionType.choices
    )

    payload = models.JSONField(
        help_text="Content depends on submission_type"
    )

    notes = models.TextField(
        blank=True,
        help_text="Student's notes when submitting"
    )

    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'submissions_submissionrevision'
        indexes = [
            models.Index(fields=['submission', 'revision_number'], name='idx_rev_subm_num'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['submission', 'revision_number'],
                name='uq_rev_subm_num'
            ),
            models.CheckConstraint(
                condition=models.Q(submission_type__in=[
                    'github_repository', 'file_upload',
                    'text_answer', 'external_link'
                ]),
                name='chk_rev_type_valid'
            ),
        ]
        ordering = ['submission', 'revision_number']

    def __str__(self):
        return f"Revision {self.revision_number} ({self.submission_type})"

    @property
    def github_url(self):
        """Extract GitHub URL from payload if type is github_repository."""
        if self.submission_type == self.SubmissionType.GITHUB_REPOSITORY:
            return self.payload.get('github_url')
        return None

    @property
    def live_url(self):
        """Extract live URL from payload."""
        if self.submission_type == self.SubmissionType.GITHUB_REPOSITORY:
            return self.payload.get('live_url')
        elif self.submission_type == self.SubmissionType.EXTERNAL_LINK:
            return self.payload.get('url')
        return None
