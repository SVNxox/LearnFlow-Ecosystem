"""
DropEnrollment Command — Student drops enrollment.
"""

from dataclasses import dataclass
from uuid import UUID

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.domain.services import EnrollmentService


@dataclass
class DropEnrollmentCommand:
    """Command to drop enrollment."""
    enrollment_id: UUID
    reason: str


class DropEnrollmentHandler:
    """Handler for DropEnrollment command."""

    @staticmethod
    def handle(command: DropEnrollmentCommand) -> CourseEnrollment:
        """
        Drop enrollment.

        Terminal action — cannot undo.

        Raises:
            CourseEnrollment.DoesNotExist: If enrollment not found
            ValidationError: If enrollment already in terminal state
        """
        enrollment = EnrollmentService.drop_enrollment(
            enrollment_id=command.enrollment_id,
            reason=command.reason
        )

        return enrollment
