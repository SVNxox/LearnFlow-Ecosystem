"""
PaymentFailed event — Critical event (Outbox Pattern).

Emitted when: Payment processing failed.
Delivery: Outbox Pattern (guaranteed delivery).
Consumers:
- Enrollment Domain (suspend enrollment)
- Notifications Domain (notify student)
"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class PaymentFailedEvent:
    """
    Event payload for PaymentFailed.

    Critical for enrollment status — must be delivered.
    """
    payment_id: UUID
    enrollment_id: UUID
    user_id: UUID
    failure_code: str
    failure_message: str
    occurred_at: datetime

    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            'payment_id': str(self.payment_id),
            'enrollment_id': str(self.enrollment_id),
            'user_id': str(self.user_id),
            'failure_code': self.failure_code,
            'failure_message': self.failure_message,
            'occurred_at': self.occurred_at.isoformat(),
        }
