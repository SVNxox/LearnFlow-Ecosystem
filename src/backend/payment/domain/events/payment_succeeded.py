"""
PaymentSucceeded event — Critical event (Outbox Pattern).

Emitted when: Payment successfully processed.
Delivery: Outbox Pattern (guaranteed delivery).
Consumers:
- Enrollment Domain (activate enrollment)
- Notifications Domain (send receipt)
- Analytics Domain (track revenue)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class PaymentSucceededEvent:
    """
    Event payload for PaymentSucceeded.

    This is a CRITICAL event that activates enrollment.
    Must use Outbox Pattern for guaranteed delivery.
    """
    payment_id: UUID
    enrollment_id: UUID
    user_id: UUID
    amount: Decimal
    currency: str
    occurred_at: datetime

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            'payment_id': str(self.payment_id),
            'enrollment_id': str(self.enrollment_id),
            'user_id': str(self.user_id),
            'amount': str(self.amount),
            'currency': self.currency,
            'occurred_at': self.occurred_at.isoformat(),
        }
