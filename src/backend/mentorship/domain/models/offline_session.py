"""
OfflineSession model
"""

import uuid

from django.db import models


class OfflineSession(models.Model):
    """
    One offline session (lesson) for a mentor group.

    Flexible scheduling — can be cancelled, rescheduled.
    """

    STATUSES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    group = models.ForeignKey(
        'mentorship.MentorGroup',
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="Mentor group for this session"
    )

    lesson_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Lesson ID (soft reference, can be NULL for custom sessions)"
    )

    module_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="Module ID (denormalized for queries)"
    )

    title = models.CharField(
        max_length=255,
        help_text="Session title (e.g., 'Занятие 5: Django ORM')"
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Session description"
    )

    scheduled_start = models.DateTimeField(
        help_text="Scheduled start time"
    )

    scheduled_end = models.DateTimeField(
        help_text="Scheduled end time"
    )

    actual_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual start time"
    )

    actual_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual end time"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='scheduled',
        help_text="Session status"
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Physical location (e.g., 'Room 301')"
    )

    meeting_url = models.TextField(
        null=True,
        blank=True,
        help_text="Online meeting URL (Zoom, Google Meet)"
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Mentor notes"
    )

    class Meta:
        db_table = 'mentorship_offlinesession'
        ordering = ['scheduled_start']
        indexes = [
            models.Index(fields=['group', 'scheduled_start'], name='idx_session_group'),
            models.Index(fields=['lesson_id', 'group'], name='idx_session_lesson'),
            models.Index(fields=['status', 'scheduled_start'], name='idx_session_status'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=[
                    'scheduled', 'in_progress', 'completed', 'cancelled', 'rescheduled'
                ]),
                name='chk_session_status'
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.scheduled_start.date()}"

    @property
    def is_completed(self) -> bool:
        """Check if session is completed."""
        return self.status == 'completed'

    @property
    def can_mark_attendance(self) -> bool:
        """Check if attendance can be marked."""
        return self.status in ['in_progress', 'completed']
