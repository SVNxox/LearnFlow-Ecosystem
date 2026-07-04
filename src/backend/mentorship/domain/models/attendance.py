"""
Attendance model
"""

import uuid

from django.db import models
from django.conf import settings


class Attendance(models.Model):
    """
    Student attendance for an offline session.

    Mentor marks attendance manually (v1).
    Attendance → LessonCompleted event (for offline students).
    """

    STATUSES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    session = models.ForeignKey(
        'mentorship.OfflineSession',
        on_delete=models.CASCADE,
        related_name='attendances',
        help_text="Session this attendance belongs to"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        help_text="Student"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        help_text="Attendance status"
    )

    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
        help_text="Mentor who marked attendance"
    )

    marked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When attendance was marked"
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Additional notes"
    )

    class Meta:
        db_table = 'mentorship_attendance'
        ordering = ['-marked_at']
        indexes = [
            models.Index(fields=['session', 'student'], name='idx_attendance_session'),
            models.Index(fields=['student', 'status'], name='idx_attendance_student'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'student'],
                name='uq_attendance_session_student'
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=['present', 'absent', 'late', 'excused']),
                name='chk_attendance_status'
            ),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} — {self.status} ({self.session.title})"

    @property
    def counts_as_present(self) -> bool:
        """Check if attendance counts as present (for lesson completion)."""
        return self.status in ['present', 'late']
