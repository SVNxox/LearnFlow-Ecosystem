"""
MyPayments Query — List user's payments.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from django.db.models import QuerySet

from src.backend.payment.domain.models import Payment


@dataclass
class MyPaymentsQuery:
    """Query to list user's payments."""
    user_id: UUID
    status: Optional[str] = None
    enrollment_id: Optional[UUID] = None


class MyPaymentsHandler:
    """Handler for MyPayments query."""

    @staticmethod
    def handle(query: MyPaymentsQuery) -> QuerySet[Payment]:
        """
        Get user's payments.

        Returns:
            QuerySet of Payment ordered by created_at DESC
        """
        filters = {
            'user_id': query.user_id,
        }

        if query.status:
            filters['status'] = query.status

        if query.enrollment_id:
            filters['enrollment_id'] = query.enrollment_id

        payments = Payment.objects.filter(
            **filters
        ).select_related('user').order_by('-created_at')

        return payments
