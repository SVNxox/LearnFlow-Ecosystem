"""
CompleteEnrollment Command — Mark enrollment as completed.
"""

from dataclasses import dataclass
from uuid import UUID

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.domain.services import EnrollmentService


@dataclass
class CompleteEnrollmentCommand:
    """Command to complete enrollment."""
    enrollment_id: UUID


class CompleteEnrollmentHandler:
    """Handler for CompleteEnrollment command."""

    @staticmethod
    def handle(command: CompleteEnrollmentCommand) -> CourseEnrollment:
        """
        Complete enrollment.

        Called by Progress Domain when course is completed.

        Raises:
            CourseEnrollment.DoesNotExist: If enrollment not found
            ValidationError: If enrollment not in ACTIVE status
        """
        enrollment = EnrollmentService.complete_enrollment(
            enrollment_id=command.enrollment_id
        )

        return enrollment
