"""
CreatePayment Command — Create payment for enrollment or course purchase.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from src.backend.payment.domain.models import Payment
from src.backend.payment.domain.services import PaymentProcessor

User = get_user_model()


@dataclass
class CreatePaymentCommand:
    """Command to create payment."""
    user_id: UUID
    enrollment_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    amount: Decimal = Decimal('0')
    currency: str = 'UZS'
    provider: str = 'stripe'
    payment_method: str = 'card'  
    idempotency_key: Optional[str] = None
    metadata: Optional[dict] = None


class CreatePaymentHandler:
    """Handler for CreatePayment command."""

    @staticmethod
    def handle(command: CreatePaymentCommand) -> Payment:
        """Create payment."""
        user = User.objects.get(id=command.user_id)

        
        valid_providers = [p[0] for p in Payment.Provider.choices]
        if command.provider not in valid_providers:
            raise ValidationError(f"Invalid provider: {command.provider}")

        
        enrollment_id = command.enrollment_id

        if not enrollment_id and command.course_id:
            from src.backend.enrollment.domain.models import CourseEnrollment
            from src.backend.learning.domain.models import Course
            from django.utils import timezone

            try:
                course = Course.objects.get(id=command.course_id, deleted_at__isnull=True)
            except Course.DoesNotExist:
                raise ValidationError(f"Course {command.course_id} not found")

            existing_enrollment = CourseEnrollment.objects.filter(
                user_id=command.user_id,
                course_id=command.course_id
            ).first()

            if existing_enrollment:
                enrollment_id = existing_enrollment.id
            else:
                enrollment = CourseEnrollment.objects.create(
                    user_id=command.user_id,
                    course_id=command.course_id,
                    status='pending',
                    delivery_format='online',
                    enrolled_at=timezone.now(),
                    payment_status='pending',
                )
                enrollment_id = enrollment.id

        if not enrollment_id:
            raise ValidationError("Either enrollment_id or course_id must be provided")

        metadata = command.metadata or {}
        if command.course_id:
            metadata['course_id'] = str(command.course_id)

        
        payment = PaymentProcessor.create_payment(
            user=user,
            enrollment_id=enrollment_id,
            amount=command.amount,
            currency=command.currency,
            provider=command.provider,
            payment_method=command.payment_method,  
            metadata=metadata,
        )

        return payment