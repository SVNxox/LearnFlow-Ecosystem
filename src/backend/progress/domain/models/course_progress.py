"""
CourseProgress Model

Tracks overall student progress through a course.
One-to-one relationship with CourseEnrollment.

According to docs/DATABASE.md and docs/design/learnflow-userprogress-review-v2.md
"""
import uuid
from django.db import models
from django.utils import timezone


class CourseProgress(models.Model):
    """
    Student progress through a course.

    Invariants:
    - One per enrollment (1:1)
    - completed_modules_count <= total_modules_count
    - completed_at IS NULL OR status = 'completed'
    """

    
    STATUS_NOT_STARTED = 'not_started'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, 'Not Started'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    enrollment_id = models.UUIDField(unique=True, db_index=True)  

    
    course_id = models.UUIDField(db_index=True)  
    user_id = models.UUIDField(db_index=True)  
    delivery_format = models.CharField(max_length=10)  
    is_sequential = models.BooleanField(default=True)  

    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED, db_index=True)
    total_modules_count = models.SmallIntegerField(default=0)  
    completed_modules_count = models.SmallIntegerField(default=0)
    cached_percentage = models.SmallIntegerField(default=0)  

    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progress_courseprogress'
        indexes = [
            models.Index(fields=['user_id', 'status'], name='idx_cp_user_status'),
            models.Index(fields=['enrollment_id'], name='idx_cp_enrollment'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(completed_modules_count__lte=models.F('total_modules_count')),
                name='chk_cprogress_modules_count'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(completed_at__isnull=True) |
                    models.Q(status='completed')
                ),
                name='chk_cprogress_completed_status'
            ),
        ]
        ordering = ['-last_activity_at']
        verbose_name = 'Course Progress'
        verbose_name_plural = 'Course Progress'

    def __str__(self):
        return f"CourseProgress({self.enrollment_id}) - {self.status}"

    @property
    def percentage(self):
        """Calculate completion percentage"""
        if self.total_modules_count == 0:
            return 0
        return int((self.completed_modules_count / self.total_modules_count) * 100)
