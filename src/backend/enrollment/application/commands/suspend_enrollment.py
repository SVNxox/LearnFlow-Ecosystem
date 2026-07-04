"""
SuspendEnrollment Command — Suspend enrollment (payment failed or admin action).
"""

from dataclasses import dataclass
from uuid import UUID

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.domain.services import EnrollmentService


@dataclass
class SuspendEnrollmentCommand:
    """Command to suspend enrollment."""
    enrollment_id: UUID
    reason: str


class SuspendEnrollmentHandler:
    """Handler for SuspendEnrollment command."""

    @staticmethod
    def handle(command: SuspendEnrollmentCommand) -> CourseEnrollment:
        """
        Suspend enrollment.

        Called by Payment Domain when payment fails or admin manually suspends.

        Raises:
            CourseEnrollment.DoesNotExist: If enrollment not found
            ValidationError: If enrollment not in PENDING or ACTIVE status
        """
        enrollment = EnrollmentService.suspend_enrollment(
            enrollment_id=command.enrollment_id,
            reason=command.reason
        )

        return enrollment
