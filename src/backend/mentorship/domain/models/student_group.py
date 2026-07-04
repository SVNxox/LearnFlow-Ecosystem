"""
StudentMentorGroup model — junction table
"""

import uuid

from django.db import models
from django.conf import settings


class StudentMentorGroup(models.Model):
    """
    Student assignment to a mentor group.

    Many-to-many relationship between students and groups.
    Only admin can add/remove students (v1).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_group_memberships',
        help_text="Student in this group"
    )

    group = models.ForeignKey(
        'mentorship.MentorGroup',
        on_delete=models.CASCADE,
        related_name='student_memberships',
        help_text="Mentor group"
    )

    enrollment_id = models.UUIDField(
        help_text="Enrollment ID (soft reference)"
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student joined the group"
    )

    left_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When student left the group"
    )

    class Meta:
        db_table = 'mentorship_studentmentorgroup'
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['student', 'group'], name='idx_student_group'),
            models.Index(fields=['group', 'joined_at'], name='idx_group_students'),
            models.Index(fields=['enrollment_id'], name='idx_membership_enrollment'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'group'],
                condition=models.Q(left_at__isnull=True),
                name='uq_active_student_group'
            ),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} in {self.group.name}"

    @property
    def is_active(self) -> bool:
        """Check if membership is active."""
        return self.left_at is None
