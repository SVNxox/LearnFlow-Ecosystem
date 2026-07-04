"""
MentorGroup model
"""

import uuid

from django.db import models
from django.conf import settings


class MentorGroup(models.Model):
    """
    Mentor group for offline learning.

    One mentor leads one group of students through a course.
    Admin assigns students to groups (v1 — no self-selection).
    """

    STATUSES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='mentor_groups',
        help_text="Mentor leading this group"
    )

    course_id = models.UUIDField(
        help_text="Course ID (soft reference)"
    )

    name = models.CharField(
        max_length=255,
        help_text="Group name (e.g., 'Python Backend 
    )

    planned_lessons_count = models.SmallIntegerField(
        help_text="Planned number of lessons"
    )

    max_students = models.SmallIntegerField(
        default=30,
        help_text="Maximum students in this group"
    )

    current_students_count = models.SmallIntegerField(
        default=0,
        help_text="Current number of students"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='active',
        help_text="Group status"
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the group started"
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the group completed"
    )

    class Meta:
        db_table = 'mentorship_mentorgroup'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mentor', 'status'], name='idx_group_mentor_status'),
            models.Index(fields=['course_id', 'status'], name='idx_group_course'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['active', 'completed', 'archived']),
                name='chk_group_status'
            ),
            models.CheckConstraint(
                condition=models.Q(current_students_count__lte=models.F('max_students')),
                name='chk_group_capacity'
            ),
        ]

    def __str__(self):
        return f"{self.name} — {self.mentor.get_full_name()}"

    @property
    def is_full(self) -> bool:
        """Check if group is at capacity."""
        return self.current_students_count >= self.max_students

    def can_add_student(self) -> bool:
        """Check if student can be added to group."""
        return self.status == 'active' and not self.is_full
