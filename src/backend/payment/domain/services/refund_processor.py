"""
RefundProcessor — Domain Service for refund processing.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from src.backend.payment.domain.models import Payment, Refund
from src.backend.payment.domain.events import RefundIssuedEvent
from src.backend.shared.infrastructure.outbox.publisher import publish_to_outbox

User = get_user_model()


class RefundProcessor:
    """
    Refund processing logic.

    Responsibilities:
    - Create refunds
    - Validate refund amounts
    - Process refund success/failure
    - Publish RefundIssued events
    """

    @staticmethod
    @transaction.atomic
    def create_refund(
        payment_id: UUID,
        amount: Decimal,
        reason: str,
        reason_details: Optional[str] = None,
        initiated_by: Optional[User] = None
    ) -> Refund:
        """
        Create refund for payment.

        Args:
            payment_id: Payment UUID
            amount: Refund amount
            reason: Refund reason (from Refund.Reason choices)
            reason_details: Additional details
            initiated_by: User who initiated refund

        Returns:
            Refund

        Raises:
            Payment.DoesNotExist: If payment not found
            ValidationError: If refund validation fails
        """
        payment = Payment.objects.select_for_update().get(pk=payment_id)

        
        if payment.status != Payment.Status.SUCCEEDED:
            raise ValidationError(
                f"Cannot refund payment with status {payment.status}. "
                "Only succeeded payments can be refunded."
            )

        
        total_refunded = payment.refunds.filter(
            status=Refund.Status.SUCCEEDED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        if total_refunded + amount > payment.amount:
            raise ValidationError(
                f"Refund amount {amount} exceeds available amount. "
                f"Payment: {payment.amount}, Already refunded: {total_refunded}, "
                f"Available: {payment.amount - total_refunded}"
            )

        
        refund = Refund.objects.create(
            payment=payment,
            amount=amount,
            reason=reason,
            reason_details=reason_details,
            status=Refund.Status.PENDING,
            initiated_by=initiated_by,
        )

        
        
        
        
        
        
        
        
        
        
        

        return refund

    @staticmethod
    @transaction.atomic
    def process_refund_succeeded(
        refund_id: UUID,
        provider_refund_id: Optional[str] = None
    ) -> Refund:
        """
        Mark refund as succeeded.

        Called from webhook handler when refund completes.

        If total refunded amount equals payment amount,
        marks payment as fully refunded and publishes RefundIssued event.

        Args:
            refund_id: Refund UUID
            provider_refund_id: Provider's refund ID

        Returns:
            Refund
        """
        refund = Refund.objects.select_for_update().get(pk=refund_id)

        
        refund.status = Refund.Status.SUCCEEDED
        refund.succeeded_at = timezone.now()

        if provider_refund_id:
            refund.provider_refund_id = provider_refund_id

        refund.save(update_fields=[
            'status', 'succeeded_at', 'provider_refund_id', 'updated_at'
        ])

        
        payment = refund.payment
        total_refunded = payment.refunds.filter(
            status=Refund.Status.SUCCEEDED
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        
        if total_refunded >= payment.amount:
            payment.status = Payment.Status.REFUNDED
            payment.refunded_at = timezone.now()
            payment.save(update_fields=['status', 'refunded_at', 'updated_at'])

            
            event = RefundIssuedEvent(
                payment_id=payment.id,
                enrollment_id=payment.enrollment_id,
                refund_amount=total_refunded,
                reason=refund.reason,
                occurred_at=timezone.now()
            )

            transaction.on_commit(
                lambda: publish_to_outbox(
                    event_type='RefundIssued',
                    aggregate_id=payment.id,
                    payload=event.to_dict()
                )
            )

        return refund

    @staticmethod
    @transaction.atomic
    def process_refund_failed(
        refund_id: UUID,
        failure_reason: str
    ) -> Refund:
        """
        Mark refund as failed.

        Args:
            refund_id: Refund UUID
            failure_reason: Why refund failed

        Returns:
            Refund
        """
        refund = Refund.objects.select_for_update().get(pk=refund_id)

        refund.status = Refund.Status.FAILED
        refund.failed_at = timezone.now()
        refund.reason_details = failure_reason
        refund.save(update_fields=[
            'status', 'failed_at', 'reason_details', 'updated_at'
        ])

        return refund
