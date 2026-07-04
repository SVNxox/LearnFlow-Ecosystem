"""
EnrollStudent Command — Enroll student in course.
"""

from dataclasses import dataclass
from uuid import UUID

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from src.backend.enrollment.domain.models import CourseEnrollment
from src.backend.enrollment.domain.services import EnrollmentService

User = get_user_model()


@dataclass
class EnrollStudentCommand:
    """Command to enroll student in course."""
    user_id: UUID
    course_id: UUID
    delivery_format: str
    payment_id: UUID = None
    enrolled_by_id: UUID = None
    access_level: str = 'full'


class EnrollStudentHandler:
    """Handler for EnrollStudent command."""

    @staticmethod
    def handle(command: EnrollStudentCommand) -> CourseEnrollment:
        """
        Execute enrollment.

        Raises:
            ValidationError: If enrollment rules violated
            User.DoesNotExist: If user not found
        """
        
        user = User.objects.get(id=command.user_id)

        
        enrolled_by = None
        if command.enrolled_by_id:
            enrolled_by = User.objects.get(id=command.enrolled_by_id)

        
        if command.delivery_format not in [
            CourseEnrollment.DeliveryFormat.ONLINE,
            CourseEnrollment.DeliveryFormat.OFFLINE,
            CourseEnrollment.DeliveryFormat.HYBRID,
        ]:
            raise ValidationError(f"Invalid delivery_format: {command.delivery_format}")

        
        if command.access_level not in [
            CourseEnrollment.AccessLevel.FULL,
            CourseEnrollment.AccessLevel.LIMITED,
            CourseEnrollment.AccessLevel.PREVIEW,
        ]:
            raise ValidationError(f"Invalid access_level: {command.access_level}")

        
        enrollment = EnrollmentService.enroll_student(
            user=user,
            course_id=command.course_id,
            delivery_format=command.delivery_format,
            payment_id=command.payment_id,
            enrolled_by=enrolled_by,
            access_level=command.access_level
        )

        return enrollment
