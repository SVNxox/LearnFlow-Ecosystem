"""
EnrollmentStatus value object.
"""

from enum import Enum


class EnrollmentStatus(str, Enum):
    """
    Enrollment lifecycle states.

    State transitions:
    pending → active → completed
       ↓         ↓
    dropped   suspended
    """

    PENDING = 'pending'       
    ACTIVE = 'active'         
    SUSPENDED = 'suspended'   
    DROPPED = 'dropped'       
    COMPLETED = 'completed'   

    @property
    def can_access(self) -> bool:
        """Can student access course in this status?"""
        return self == EnrollmentStatus.ACTIVE

    @property
    def is_terminal(self) -> bool:
        """Is this a terminal state (no further transitions)?"""
        return self in [EnrollmentStatus.DROPPED, EnrollmentStatus.COMPLETED]

    @property
    def requires_payment(self) -> bool:
        """Does this status require payment processing?"""
        return self == EnrollmentStatus.PENDING

    def can_transition_to(self, new_status: 'EnrollmentStatus') -> bool:
        """Check if transition to new status is allowed."""
        
        if self.is_terminal:
            return False

        
        allowed_transitions = {
            EnrollmentStatus.PENDING: [
                EnrollmentStatus.ACTIVE,
                EnrollmentStatus.DROPPED,
                EnrollmentStatus.SUSPENDED,
            ],
            EnrollmentStatus.ACTIVE: [
                EnrollmentStatus.COMPLETED,
                EnrollmentStatus.DROPPED,
                EnrollmentStatus.SUSPENDED,
            ],
            EnrollmentStatus.SUSPENDED: [
                EnrollmentStatus.ACTIVE,
                EnrollmentStatus.DROPPED,
            ],
        }

        return new_status in allowed_transitions.get(self, [])
