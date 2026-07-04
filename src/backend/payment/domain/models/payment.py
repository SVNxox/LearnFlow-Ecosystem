"""
Payment model — Aggregate Root for Payment Domain.

ADR-032: Payment Domain extracted as separate bounded context.
This domain handles all financial transactions: payments, refunds, reconciliation.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """
    Payment transaction — Aggregate Root of Payment Domain.

    Responsibilities:
    - Payment lifecycle (pending → succeeded/failed)
    - Link to enrollment
    - Provider-specific data (Stripe, Payme)
    - Idempotency guarantees
    - Financial audit trail

    Design choices:
    - Immutable after terminal state (succeeded/failed/refunded)
    - All state changes logged in PaymentTransaction
    - Idempotency key prevents duplicate charges
    - PCI compliance: only store last4 + brand, never full card
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        PAYME = "payme", "Payme.uz"
        CLICK = "click", "Click.uz"
        MANUAL = "manual", "Manual"  

    class PaymentMethod(models.TextChoices):
        CARD = "card", "Credit/Debit Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CASH = "cash", "Cash"
        CLICK = "click", "Click (Uzbekistan)"
        PAYME = "payme", "Payme (Uzbekistan)"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='payments',
        db_index=True
    )
    enrollment_id = models.UUIDField(db_index=True)  

    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Payment amount"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="ISO 4217 currency code"
    )

    
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices
    )

    
    provider_payment_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="Payment ID from provider (Stripe, Payme)"
    )
    provider_customer_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Customer ID from provider"
    )

    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        null=True,
        blank=True
    )

    
    card_last4 = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        help_text="Last 4 digits of card (PCI compliant)"
    )
    card_brand = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Card brand (visa, mastercard, amex)"
    )

    
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        help_text="Prevents duplicate charges"
    )

    
    metadata = models.JSONField(
        default=dict,
        help_text="Flexible storage for provider-specific data"
    )

    
    failure_code = models.CharField(max_length=50, null=True, blank=True)
    failure_message = models.TextField(null=True, blank=True)

    
    succeeded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payment_payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_payment_user_status'),
            models.Index(fields=['enrollment_id'], name='idx_payment_enrollment'),
            models.Index(fields=['provider_payment_id'], name='idx_payment_provider_id'),
            models.Index(fields=['idempotency_key'], name='idx_payment_idempotency'),
            models.Index(fields=['status', 'created_at'], name='idx_payment_status_created'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='chk_payment_amount_positive'
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=['pending', 'processing', 'succeeded', 'failed', 'cancelled', 'refunded']
                ),
                name='chk_payment_status'
            ),
        ]

    def __str__(self) -> str:
        return f"Payment {self.id} ({self.amount} {self.currency}) - {self.status}"

    def is_terminal(self) -> bool:
        """Check if payment is in terminal state (no further transitions)."""
        return self.status in [
            self.Status.SUCCEEDED,
            self.Status.FAILED,
            self.Status.CANCELLED,
            self.Status.REFUNDED
        ]

    def clean(self):
        """Validate payment data."""
        if self.amount <= 0:
            raise ValidationError("Payment amount must be positive")

        if len(self.currency) != 3:
            raise ValidationError("Currency must be ISO 4217 code (3 letters)")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
