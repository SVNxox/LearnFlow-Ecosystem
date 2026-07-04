"""
PaymentProcessor — Core Domain Service for payment processing.
"""

import time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from src.backend.payment.domain.models import Payment, PaymentTransaction, Refund
from src.backend.payment.domain.events import (
    PaymentSucceededEvent,
    PaymentFailedEvent,
)
from src.backend.shared.infrastructure.outbox.publisher import publish_to_outbox

User = get_user_model()


class PaymentProcessor:
    """
    Core payment processing logic.

    Responsibilities:
    - Create payment intents
    - Process payment webhooks
    - Handle success/failure transitions
    - Publish critical events (Outbox Pattern)
    """

    @staticmethod
    @transaction.atomic
    def create_payment(
        user: User,
        enrollment_id: UUID,
        amount: Decimal,
        currency: str = 'USD',
        provider: str = 'stripe',
        payment_method: str = 'card',
        metadata: dict = None
    ) -> Payment:
        """
        Create payment intent.

        Args:
            user: User making payment
            enrollment_id: Enrollment being paid for
            amount: Payment amount
            currency: ISO 4217 currency code
            provider: Payment provider (stripe/payme/manual)
            metadata: Additional metadata

        Returns:
            Payment

        Raises:
            ValidationError: If payment validation fails
        """
        
        idempotency_key = f"{user.id}:{enrollment_id}:{int(time.time())}"

        valid_providers = [p[0] for p in Payment.Provider.choices]
        if provider not in valid_providers:
            raise ValidationError(f"Invalid provider: {provider}. Must be one of {valid_providers}")

        
        valid_methods = [m[0] for m in Payment.PaymentMethod.choices]
        if payment_method not in valid_methods:
            raise ValidationError(f"Invalid payment_method: {payment_method}. Must be one of {valid_methods}")

        
        payment = Payment.objects.create(
            user=user,
            enrollment_id=enrollment_id,
            amount=amount,
            currency=currency,
            provider=provider,
            payment_method=payment_method,
            status=Payment.Status.PENDING,
            idempotency_key=idempotency_key,
            metadata=metadata or {},
        )

        
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TransactionType.CREATED,
            amount=amount,
            transaction_id=f"{payment.id}:created",
        )

        
        
        
        
        
        
        

        return payment

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    @staticmethod
    def process_succeeded(provider_payment_id: str, provider_data: dict = None) -> Payment:
        """
        Process successful payment.
        Обновляет статус платежа и активирует enrollment.
        """
        from src.backend.enrollment.domain.models import CourseEnrollment

        with transaction.atomic():
            try:
                payment = Payment.objects.select_for_update().get(
                    provider_payment_id=provider_payment_id
                )
            except Payment.DoesNotExist:
                logger.warning(f"Payment with provider_payment_id={provider_payment_id} not found")
                raise

            
            payment.status = Payment.Status.SUCCEEDED
            payment.succeeded_at = timezone.now()
            payment.provider_response = provider_data or {}
            payment.save(update_fields=['status', 'succeeded_at', 'provider_response'])

            
            if payment.enrollment_id:
                try:
                    enrollment = CourseEnrollment.objects.select_for_update().get(
                        id=payment.enrollment_id
                    )

                    if enrollment.status in ['pending', 'inactive']:
                        enrollment.status = 'active'
                        enrollment.payment_status = 'paid'
                        enrollment.save(update_fields=['status', 'payment_status'])

                        logger.info(
                            f"Enrollment {enrollment.id} activated for user {enrollment.user_id} "
                            f"and course {enrollment.course_id}"
                        )
                except CourseEnrollment.DoesNotExist:
                    logger.error(f"Enrollment {payment.enrollment_id} not found")

            return payment

    @staticmethod
    def process_failed(provider_payment_id: str, failure_reason: str = '') -> Payment:
        """
        Process failed payment.
        """
        with transaction.atomic():
            try:
                payment = Payment.objects.select_for_update().get(
                    provider_payment_id=provider_payment_id
                )
            except Payment.DoesNotExist:
                logger.warning(f"Payment with provider_payment_id={provider_payment_id} not found")
                raise

            payment.status = Payment.Status.FAILED
            payment.failed_at = timezone.now()
            payment.failure_message = failure_reason
            payment.save(update_fields=['status', 'failed_at', 'failure_message'])

            return payment

    @staticmethod
    @transaction.atomic
    def process_payment_failed(
            payment_id: UUID,
            failure_code: str,
            failure_message: str,
            provider_response: Optional[dict] = None
    ) -> Payment:
        """Mark payment as failed."""
        payment = Payment.objects.select_for_update().get(pk=payment_id)

        if payment.is_terminal():
            return payment

        payment.status = Payment.Status.FAILED
        payment.failed_at = timezone.now()
        payment.failure_code = failure_code
        payment.failure_message = failure_message
        payment.save(update_fields=[
            'status', 'failed_at', 'failure_code',
            'failure_message', 'updated_at'
        ])

        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type=PaymentTransaction.TransactionType.FAILED,
            amount=payment.amount,
            transaction_id=f"{payment.id}:failed",
            provider_response=provider_response,
        )

        event = PaymentFailedEvent(
            payment_id=payment.id,
            enrollment_id=payment.enrollment_id,
            user_id=payment.user_id,
            failure_code=failure_code,
            failure_message=failure_message,
            occurred_at=timezone.now()
        )

        transaction.on_commit(
            lambda: publish_to_outbox(
                event_type='PaymentFailed',
                aggregate_id=payment.id,
                payload=event.to_dict()
            )
        )

        return payment