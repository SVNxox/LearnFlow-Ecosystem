"""
PaymentTransaction model — Immutable audit log of payment state changes.
"""

import uuid

from django.db import models


class PaymentTransaction(models.Model):
    """
    Immutable audit log of all payment state changes.

    Every status change creates a new transaction record.
    Provides complete financial audit trail.

    Design choices:
    - Immutable records (no updates, only inserts)
    - Idempotent via transaction_id
    - Stores provider responses for debugging
    """

    class TransactionType(models.TextChoices):
        CREATED = "created", "Created"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    payment = models.ForeignKey(
        'Payment',
        on_delete=models.PROTECT,
        related_name='transactions'
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    
    provider_response = models.JSONField(
        null=True,
        blank=True,
        help_text="Raw response from payment provider"
    )

    
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique transaction ID (payment_id:type format)"
    )

    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_transaction'
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment', 'created_at'], name='idx_transaction_payment'),
            models.Index(fields=['transaction_type', 'created_at'], name='idx_transaction_type'),
        ]

    def __str__(self) -> str:
        return f"Transaction {self.transaction_type} for Payment {self.payment_id}"
