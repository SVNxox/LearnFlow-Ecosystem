"""
PaymentDetail Query — Get payment details.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.backend.payment.domain.models import Payment


@dataclass
class PaymentDetailQuery:
    """Query to get payment details."""
    payment_id: UUID
    user_id: Optional[UUID] = None  


class PaymentDetailHandler:
    """Handler for PaymentDetail query."""

    @staticmethod
    def handle(query: PaymentDetailQuery) -> Payment:
        """
        Get payment details.

        Raises:
            Payment.DoesNotExist: If payment not found
            PermissionError: If user_id provided and doesn't match payment
        """
        payment = Payment.objects.select_related('user').get(
            id=query.payment_id
        )

        
        if query.user_id and payment.user_id != query.user_id:
            raise PermissionError("You don't have permission to view this payment")

        return payment
