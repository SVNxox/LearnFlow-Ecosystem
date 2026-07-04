"""
CourseEnrollment model — User × Course membership.

ADR-032: Extracted from Learning Domain into separate Enrollment Domain.
This model is the Integration Hub for Payment → Enrollment → Progress → Certificates.
"""

import uuid
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class CourseEnrollment(models.Model):
    """
    User × Course membership — Aggregate Root of Enrollment Domain.

    Responsibilities:
    - Access Control: who can access which course
    - Contract Terms: delivery format, dates, payment status
    - Enrollment Lifecycle: pending → active → suspended → dropped → completed
    - Integration Hub: connects Payment, Progress, Certificates domains

    Named explicitly (not just "Enrollment") to distinguish from future
    MentorGroupEnrollment, EventEnrollment, CertificationEnrollment, etc.

    Key design choices
    ------------------
    * delivery_format lives HERE, not on Course.
      One course can have online and offline students simultaneously.
    * on_delete=PROTECT for user: don't silently drop enrollments on account
      deletion; handle explicitly via signal (set status=dropped, then anonymise).
    * Soft reference to Course (course_id UUIDField, no FK) — see ADR-032.
      We read Course data via queries, not through FK relationships.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"  
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"  
        DROPPED = "dropped", "Dropped"
        COMPLETED = "completed", "Completed"

    class DeliveryFormat(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"
        HYBRID = "hybrid", "Hybrid"

    class AccessLevel(models.TextChoices):
        FULL = "full", "Full"
        LIMITED = "limited", "Limited"
        PREVIEW = "preview", "Preview"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="course_enrollments",
        db_index=True,
    )
    
    course_id = models.UUIDField(db_index=True)

    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    delivery_format = models.CharField(
        max_length=10,
        choices=DeliveryFormat.choices
    )
    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.FULL
    )

    
    payment_id = models.UUIDField(null=True, blank=True, db_index=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    enrolled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="enrollments_created",
        help_text="Null = self-enrolled. Non-null = admin/mentor enrolled this student.",
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="When access begins"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="When access expires"
    )

    
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_reason = models.TextField(null=True, blank=True)

    
    dropped_at = models.DateTimeField(null=True, blank=True)
    dropped_reason = models.TextField(null=True, blank=True)

    
    completed_at = models.DateTimeField(null=True, blank=True)

    
    deleted_at = models.DateTimeField(null=True, blank=True)

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollment_courseenrollment"
        verbose_name = "Course Enrollment"
        verbose_name_plural = "Course Enrollments"
        indexes = [
            
            models.Index(
                fields=["user_id", "status"],
                name="idx_enrollment_user_status",
            ),
            
            models.Index(
                fields=["course_id", "status"],
                name="idx_enrollment_course_status",
            ),
            
            models.Index(
                fields=["payment_id"],
                name="idx_enrollment_payment",
            ),
            
            models.Index(
                fields=["status", "deleted_at"],
                name="idx_enrollment_status_deleted",
            ),
        ]
        constraints = [
            
            models.UniqueConstraint(
                fields=["user_id", "course_id"],
                name="uq_enrollment_user_course",
            ),
            models.CheckConstraint(
                condition=Q(status__in=["pending", "active", "suspended", "dropped", "completed"]),
                name="chk_enrollment_status",
            ),
            models.CheckConstraint(
                condition=Q(delivery_format__in=["online", "offline", "hybrid"]),
                name="chk_enrollment_delivery_format",
            ),
            models.CheckConstraint(
                condition=Q(payment_status__in=["pending", "paid", "failed", "refunded"]),
                name="chk_enrollment_payment_status",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.email if hasattr(self, 'user') else self.user_id} → Course({self.course_id})"

    def can_access_course(self) -> bool:
        """
        Business rule: Check if student has access to course.

        BR-01: Status must be active
        BR-02: Payment must be paid or pending (free courses)
        BR-03: Must be within date range (if set)
        BR-04: Not soft-deleted
        """
        if self.deleted_at:
            return False

        if self.status != self.Status.ACTIVE:
            return False

        if self.payment_status not in [self.PaymentStatus.PAID, self.PaymentStatus.PENDING]:
            return False

        
        now = timezone.now().date()
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False

        return True

    def is_expired(self) -> bool:
        """Check if enrollment has expired."""
        if not self.end_date:
            return False
        return timezone.now().date() > self.end_date

    def is_terminal_status(self) -> bool:
        """Check if status is terminal (cannot transition further)."""
        return self.status in [self.Status.DROPPED, self.Status.COMPLETED]
