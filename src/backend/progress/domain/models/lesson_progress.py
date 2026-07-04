"""
LessonProgress Model

Tracks student progress through a lesson.
Includes content gate and homework gate tracking.

According to docs/DATABASE.md and docs/design/learnflow-userprogress-review-v2.md
"""
import uuid
from django.db import models
from django.utils import timezone


class LessonProgress(models.Model):
    """
    Lesson-level progress tracking.

    Gates:
    - Content gate: viewed_required_count >= required_content_count
    - Homework gate: homework_submitted = True (if homework_required)

    Status flow: locked → unlocked → in_progress → completed
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    enrollment_id = models.UUIDField(db_index=True)
    lesson_id = models.UUIDField(db_index=True)
    module_id = models.UUIDField()  
    course_id = models.UUIDField()  

    
    lesson_order = models.SmallIntegerField()
    module_order = models.SmallIntegerField()  

    
    STATUS_CHOICES = [
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='locked')

    # Completion source tracking
    COMPLETION_SOURCE_CHOICES = [
        ('student_activity', 'Student Activity'),
        ('mentor_attendance', 'Mentor Attendance'),
        ('mentor_override', 'Mentor Override'),
        ('admin_override', 'Admin Override'),
    ]
    completion_source = models.CharField(
        max_length=30,
        choices=COMPLETION_SOURCE_CHOICES,
        null=True,
        blank=True
    )

    # Content gate (snapshots from Learning Domain)
    required_content_count = models.SmallIntegerField(default=0)
    viewed_required_count = models.SmallIntegerField(default=0)

    # Homework gate
    homework_required = models.BooleanField(default=False)
    homework_submitted = models.BooleanField(default=False)
    homework_submitted_at = models.DateTimeField(null=True, blank=True)

    # Flags
    is_stale = models.BooleanField(default=False)  # Lesson deleted
    is_active = models.BooleanField(default=True)   # Enrollment active

    # Override audit trail (F20 fix from review)
    override_by_id = models.UUIDField(null=True, blank=True)
    override_reason = models.TextField(null=True, blank=True)

    # Timestamps
    unlocked_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'progress_lessonprogress'
        unique_together = [('enrollment_id', 'lesson_id')]
        indexes = [
            # F8 fix: module_order + lesson_order for get_next_action
            models.Index(
                fields=['enrollment_id', 'module_order', 'lesson_order'],
                name='idx_lp_enr_mod_lesson',
                condition=models.Q(
                    status__in=['unlocked', 'in_progress'],
                    is_stale=False,
                    is_active=True
                )
            ),
            models.Index(fields=['enrollment_id', 'status']),
            models.Index(fields=['lesson_id']),
            models.Index(fields=['module_id']),
        ]
        ordering = ['module_order', 'lesson_order']
        constraints = [
            # F2 fix: removed +1 tolerance
            models.CheckConstraint(
                condition=models.Q(viewed_required_count__lte=models.F('required_content_count')),
                name='chk_lp_viewed_lte_required'
            ),
            models.CheckConstraint(
                condition=models.Q(
                    models.Q(completed_at__isnull=True) | models.Q(status='completed')
                ),
                name='chk_lp_completed_at_consistency'
            ),
        ]

    def __str__(self):
        return f"LessonProgress(enrollment={self.enrollment_id}, lesson={self.lesson_id}, status={self.status})"

    def content_gate_passed(self) -> bool:
        """Check if content gate is satisfied."""
        return self.viewed_required_count >= self.required_content_count

    def homework_gate_passed(self) -> bool:
        """Check if homework gate is satisfied."""
        if not self.homework_required:
            return True
        return self.homework_submitted

    def can_complete(self) -> bool:
        """Check if lesson can be marked completed."""
        return self.content_gate_passed() and self.homework_gate_passed()
