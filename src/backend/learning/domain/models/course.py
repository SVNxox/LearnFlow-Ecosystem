"""
Course model — top-level learning container.
"""

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel


class Course(SoftDeleteModel):
    """
    Top-level learning container.

    Delivery mode is NOT stored here — each CourseEnrollment carries its
    own delivery_format.  This table only declares which formats the course
    *supports* via the boolean flags supports_online / supports_offline.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)
    thumbnail_url = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        "learning.CourseCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="learning",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    supports_online = models.BooleanField(default=True)
    supports_offline = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default="ru")
    estimated_weeks = models.SmallIntegerField(null=True, blank=True)
    is_sequential = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_courses",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Course price (0 for free courses)"
    )
    currency = models.CharField(
        max_length=3,
        default='UZS',
        choices=[('UZS', 'UZS'), ('USD', 'USD')]
    )

    class Meta:
        db_table = "courses_course"
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            
            models.Index(
                fields=["status"],
                condition=Q(deleted_at__isnull=True),
                name="idx_course_status",
            ),
            
            models.Index(
                fields=["category_id"],
                condition=Q(deleted_at__isnull=True),
                name="idx_course_category",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["draft", "published", "archived"]),
                name="chk_course_status",
            ),
            models.CheckConstraint(
                condition=Q(estimated_weeks__isnull=True) | Q(estimated_weeks__gt=0),
                name="chk_course_weeks",
            ),
            
            models.CheckConstraint(
                condition=Q(supports_online=True) | Q(supports_offline=True),
                name="chk_course_delivery",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def get_enrollments(self):
        """
        Soft reference to CourseEnrollment via course_id.

        Since Enrollment Domain uses soft references (ADR-032),
        we query enrollments by course_id instead of FK.

        Returns:
            QuerySet of CourseEnrollment instances for this course
        """
        from src.backend.enrollment.models import CourseEnrollment
        return CourseEnrollment.objects.filter(course_id=self.id)
