"""
CourseCategory model — hierarchical catalog taxonomy.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from .base import TimestampedModel


class CourseCategory(TimestampedModel):
    """
    Hierarchical catalog taxonomy.

    Two levels only: root categories (Backend, Frontend) and subcategories
    (Django, FastAPI under Backend).  Application enforces max depth = 2.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        db_index=True,
    )
    description = models.CharField(max_length=500, null=True, blank=True)
    icon = models.CharField(max_length=500, null=True, blank=True)
    order = models.SmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "courses_coursecategory"
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"
        ordering = ["order", "name"]
        indexes = [
            
            models.Index(
                fields=["parent_id", "order"],
                condition=Q(is_active=True),
                name="idx_category_root",
            ),
        ]

    

    def clean(self):
        """Enforce max 2 levels of hierarchy."""
        if self.parent_id and self.parent.parent_id is not None:
            raise ValidationError(
                "Categories support a maximum depth of 2 levels "
                "(root + one subcategory)."
            )

    def __str__(self) -> str:
        return self.name
