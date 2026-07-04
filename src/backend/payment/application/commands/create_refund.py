"""
CreateRefund Command — Create refund for payment.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model

from src.backend.payment.domain.models import Refund
from src.backend.payment.domain.services import RefundProcessor

User = get_user_model()


@dataclass
class CreateRefundCommand:
    """Command to create refund."""
    payment_id: UUID
    amount: Decimal
    reason: str
    reason_details: Optional[str] = None
    initiated_by_id: Optional[UUID] = None


class CreateRefundHandler:
    """Handler for CreateRefund command."""

    @staticmethod
    def handle(command: CreateRefundCommand) -> Refund:
        """
        Create refund.

        Raises:
            Payment.DoesNotExist: If payment not found
            ValidationError: If refund validation fails
        """
        
        initiated_by = None
        if command.initiated_by_id:
            initiated_by = User.objects.get(id=command.initiated_by_id)

        
        refund = RefundProcessor.create_refund(
            payment_id=command.payment_id,
            amount=command.amount,
            reason=command.reason,
            reason_details=command.reason_details,
            initiated_by=initiated_by,
        )

        return refund
