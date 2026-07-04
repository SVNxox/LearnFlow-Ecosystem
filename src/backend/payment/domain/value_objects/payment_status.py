"""
PaymentStatus value object.
"""

from enum import Enum


class PaymentStatus(str, Enum):
    """
    Payment status lifecycle.

    State transitions:
    pending → processing → succeeded
    pending → processing → failed
    pending → cancelled
    succeeded → refunded
    """

    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

    @property
    def is_terminal(self) -> bool:
        """Is this a terminal state (no further transitions)?"""
        return self in [
            PaymentStatus.SUCCEEDED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELLED,
            PaymentStatus.REFUNDED
        ]

    @property
    def can_be_refunded(self) -> bool:
        """Can payment in this status be refunded?"""
        return self == PaymentStatus.SUCCEEDED

    def can_transition_to(self, new_status: 'PaymentStatus') -> bool:
        """Check if transition to new status is allowed."""
        
        if self.is_terminal and new_status != PaymentStatus.REFUNDED:
            return False

        
        allowed_transitions = {
            PaymentStatus.PENDING: [
                PaymentStatus.PROCESSING,
                PaymentStatus.CANCELLED,
            ],
            PaymentStatus.PROCESSING: [
                PaymentStatus.SUCCEEDED,
                PaymentStatus.FAILED,
            ],
            PaymentStatus.SUCCEEDED: [
                PaymentStatus.REFUNDED,
            ],
        }

        return new_status in allowed_transitions.get(self, [])
