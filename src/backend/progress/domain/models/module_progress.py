"""
ModuleProgress Model

Tracks student progress through a module.

According to docs/DATABASE.md and docs/design/learnflow-userprogress-review-v2.md
"""
import uuid
from django.db import models
from django.utils import timezone


class ModuleProgress(models.Model):
    """
    Student progress through a module.

    Invariants:
    - completed_lessons_count <= total_lessons_count
    - completed_at IS NULL OR status = 'completed'
    - status = 'assessment_pending' → assessment_required = True
    """

    
    STATUS_LOCKED = 'locked'
    STATUS_UNLOCKED = 'unlocked'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_ASSESSMENT_PENDING = 'assessment_pending'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_LOCKED, 'Locked'),
        (STATUS_UNLOCKED, 'Unlocked'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_ASSESSMENT_PENDING, 'Assessment Pending'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    enrollment_id = models.UUIDField(db_index=True)  # → enrollment.CourseEnrollment
    module_id = models.UUIDField(db_index=True)  # → learning.Module

    # Denormalized
    course_id = models.UUIDField(db_index=True)  # → learning.Course
    module_order = models.SmallIntegerField()  # Snapshot from Module

    # Progress tracking
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default=STATUS_LOCKED, db_index=True)
    total_lessons_count = models.SmallIntegerField(default=0)  # Snapshot
    completed_lessons_count = models.SmallIntegerField(default=0)

    # Assessment gate
    assessment_required = models.BooleanField(default=False)  # Snapshot
    assessment_passed = models.BooleanField(default=False)
    assessment_passed_at = models.DateTimeField(null=True, blank=True)

    # Staleness flag (module deleted)
    is_stale = models.BooleanField(default=False, db_index=True)

    # Timestamps
    unlocked_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progress_moduleprogress'
        indexes = [
            models.Index(fields=['enrollment_id', 'module_order'], name='idx_mp_enr_order'),
            models.Index(fields=['enrollment_id', 'status'], name='idx_mp_enr_status'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment_id', 'module_id'],
                name='uq_moduleprogress_enr_module'
            ),
            models.CheckConstraint(
                condition=models.Q(completed_lessons_count__lte=models.F('total_lessons_count')),
                name='chk_mprogress_lessons_count'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(completed_at__isnull=True) |
                    models.Q(status='completed')
                ),
                name='chk_mprogress_completed_status'
            ),
        ]
        ordering = ['enrollment_id', 'module_order']
        verbose_name = 'Module Progress'
        verbose_name_plural = 'Module Progress'

    def __str__(self):
        return f"ModuleProgress(module={self.module_id}, status={self.status})"

    @property
    def percentage(self):
        """Calculate completion percentage"""
        if self.total_lessons_count == 0:
            return 0
        return int((self.completed_lessons_count / self.total_lessons_count) * 100)
