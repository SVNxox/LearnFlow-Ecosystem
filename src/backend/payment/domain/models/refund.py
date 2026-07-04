"""
Refund model — Refunds for payments.
"""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Refund(models.Model):
    """
    Refund for a payment.

    A payment can have multiple partial refunds.
    Total refunded amount cannot exceed payment amount.

    Design choices:
    - Partial refunds supported
    - Status tracking (pending → succeeded)
    - Audit trail via initiated_by
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    class Reason(models.TextChoices):
        DUPLICATE = "duplicate", "Duplicate"
        FRAUDULENT = "fraudulent", "Fraudulent"
        REQUESTED_BY_CUSTOMER = "requested_by_customer", "Requested by customer"
        COURSE_CANCELLED = "course_cancelled", "Course cancelled"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    payment = models.ForeignKey(
        'Payment',
        on_delete=models.PROTECT,
        related_name='refunds'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Refund amount"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    reason = models.CharField(
        max_length=100,
        choices=Reason.choices
    )

    reason_details = models.TextField(
        null=True,
        blank=True,
        help_text="Additional details about refund reason"
    )

    
    provider_refund_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Refund ID from provider"
    )

    
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='refunds_initiated'
    )

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_refund'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        indexes = [
            models.Index(fields=['payment', 'status'], name='idx_refund_payment_status'),
            models.Index(fields=['provider_refund_id'], name='idx_refund_provider_id'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='chk_refund_amount_positive'
            ),
        ]

    def __str__(self) -> str:
        return f"Refund {self.id} ({self.amount}) - {self.status}"

    def clean(self):
        """Validate refund data."""
        if self.amount <= 0:
            raise ValidationError("Refund amount must be positive")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
