"""
AccessRule model — Rules for accessing course content.

Examples:
- Course becomes available 3 days after enrollment
- Module 2 unlocks only after Module 1 completion
- Bonus content available only for paid students
- Offline-only content not accessible to online students
"""

import uuid

from django.db import models


class AccessRule(models.Model):
    """
    Access rules for course content.

    Provides fine-grained control over when and how students can access
    specific resources (courses, modules, lessons, content).

    Design choices:
    - JSONB rule_config for flexibility (different rules need different data)
    - Soft reference to resource (resource_id UUID, no FK)
    - Multiple rules can apply to same resource (checked in order)
    """

    class ResourceType(models.TextChoices):
        COURSE = "course", "Course"
        MODULE = "module", "Module"
        LESSON = "lesson", "Lesson"
        CONTENT = "content", "Content"

    class RuleType(models.TextChoices):
        TIME_BASED = "time_based", "Time-based"
        PREREQUISITE = "prerequisite", "Prerequisite"
        PAYMENT_TIER = "payment_tier", "Payment Tier"
        DELIVERY_FORMAT = "delivery_format", "Delivery Format"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    enrollment = models.ForeignKey(
        'CourseEnrollment',
        on_delete=models.CASCADE,
        related_name='access_rules'
    )

    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices
    )
    resource_id = models.UUIDField(db_index=True)  

    rule_type = models.CharField(
        max_length=30,
        choices=RuleType.choices
    )

    
    rule_config = models.JSONField(default=dict)
    
    
    
    
    

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollment_accessrule'
        verbose_name = 'Access Rule'
        verbose_name_plural = 'Access Rules'
        indexes = [
            models.Index(
                fields=['enrollment', 'resource_type', 'is_active'],
                name='idx_accessrule_enr_type',
            ),
            models.Index(
                fields=['resource_id', 'is_active'],
                name='idx_accessrule_resource',
            ),
        ]

    def __str__(self) -> str:
        return f"{self.rule_type} rule for {self.resource_type}({self.resource_id})"
