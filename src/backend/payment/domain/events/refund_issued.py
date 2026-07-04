"""
RefundIssued event — Critical event (Outbox Pattern).

Emitted when: Full refund issued for payment.
Delivery: Outbox Pattern (guaranteed delivery).
Consumers:
- Enrollment Domain (drop enrollment)
- Notifications Domain (notify student)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class RefundIssuedEvent:
    """
    Event payload for RefundIssued.

    Critical — triggers enrollment termination.
    """
    payment_id: UUID
    enrollment_id: UUID
    refund_amount: Decimal
    reason: str
    occurred_at: datetime

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            'payment_id': str(self.payment_id),
            'enrollment_id': str(self.enrollment_id),
            'refund_amount': str(self.refund_amount),
            'reason': self.reason,
            'occurred_at': self.occurred_at.isoformat(),
        }
