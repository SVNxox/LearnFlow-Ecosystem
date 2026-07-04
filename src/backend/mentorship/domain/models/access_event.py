"""
AccessEvent model — турникет events (analytics only)
"""

import uuid

from django.db import models
from django.conf import settings


class AccessEvent(models.Model):
    """
    Physical access events from turnstile (face ID, RFID, etc).

    Used for analytics and attendance hints, NOT for lesson completion.
    Mentor is the source of truth for attendance (ADR-021).
    """

    SOURCES = [
        ('face_id', 'Face ID'),
        ('rfid', 'RFID Card'),
        ('turnstile', 'Turnstile'),
        ('manual', 'Manual Entry'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='access_events',
        help_text="Student who accessed"
    )

    entered_at = models.DateTimeField(
        help_text="When student entered"
    )

    exited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student exited"
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCES,
        help_text="Access source"
    )

    device_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Device ID (turnstile, face_id reader)"
    )

    location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Location (building, floor)"
    )

    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata"
    )

    class Meta:
        db_table = 'mentorship_accessevent'
        ordering = ['-entered_at']
        indexes = [
            models.Index(fields=['student', 'entered_at'], name='idx_access_student'),
            models.Index(fields=['entered_at'], name='idx_access_time'),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} — {self.entered_at}"
