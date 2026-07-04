"""
ActivateEnrollment Command — Activate enrollment after payment.
"""

from dataclasses import dataclass
from uuid import UUID

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.domain.services import EnrollmentService


@dataclass
class ActivateEnrollmentCommand:
    """Command to activate enrollment."""
    enrollment_id: UUID
    payment_id: UUID


class ActivateEnrollmentHandler:
    """Handler for ActivateEnrollment command."""

    @staticmethod
    def handle(command: ActivateEnrollmentCommand) -> CourseEnrollment:
        """
        Activate enrollment after successful payment.

        Called by Payment Domain event handler.

        Raises:
            CourseEnrollment.DoesNotExist: If enrollment not found
            ValidationError: If enrollment not in PENDING status
        """
        enrollment = EnrollmentService.activate_enrollment(
            enrollment_id=command.enrollment_id,
            payment_id=command.payment_id
        )

        return enrollment
