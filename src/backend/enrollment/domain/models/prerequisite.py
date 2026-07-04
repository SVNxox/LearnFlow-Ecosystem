"""
EnrollmentPrerequisite model — Prerequisites for enrolling in a course.

Examples:
- "Backend Advanced" requires "Python Fundamentals" completion
- "Backend Advanced" requires "Final Project" score >= 70
- "Backend Advanced" requires "Junior Certificate"
"""

import uuid

from django.db import models


class EnrollmentPrerequisite(models.Model):
    """
    Prerequisites for enrolling in a course.

    Design choices:
    - Soft reference to target course (course_id UUID, no FK)
    - JSONB prerequisite_config for flexibility
    - is_required flag allows optional prerequisites (recommendations)
    - order field for display priority
    """

    class PrerequisiteType(models.TextChoices):
        COURSE = "course", "Course Completion"
        ASSESSMENT = "assessment", "Assessment Score"
        CERTIFICATE = "certificate", "Certificate"
        CUSTOM = "custom", "Custom Rule"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    course_id = models.UUIDField(db_index=True)

    prerequisite_type = models.CharField(
        max_length=20,
        choices=PrerequisiteType.choices
    )

    
    prerequisite_config = models.JSONField(default=dict)
    
    
    
    
    

    is_required = models.BooleanField(
        default=True,
        help_text="False = recommendation only, True = hard requirement"
    )

    order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Display order (lower = higher priority)"
    )

    description = models.TextField(
        blank=True,
        help_text="Human-readable description shown to students"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollment_prerequisite'
        verbose_name = 'Enrollment Prerequisite'
        verbose_name_plural = 'Enrollment Prerequisites'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(
                fields=['course_id', 'is_required'],
                name='idx_prereq_course_required',
            ),
        ]

    def __str__(self) -> str:
        required_text = "Required" if self.is_required else "Recommended"
        return f"{required_text} {self.prerequisite_type} for Course({self.course_id})"

    def get_display_name(self) -> str:
        """Human-readable prerequisite name."""
        if self.description:
            return self.description

        if self.prerequisite_type == self.PrerequisiteType.COURSE:
            return f"Course completion required"
        elif self.prerequisite_type == self.PrerequisiteType.ASSESSMENT:
            min_score = self.prerequisite_config.get('min_score', 70)
            return f"Assessment score >= {min_score}%"
        elif self.prerequisite_type == self.PrerequisiteType.CERTIFICATE:
            level = self.prerequisite_config.get('required_certificate_level', 'any')
            return f"{level.title()} certificate required"
        else:
            return "Custom requirement"
