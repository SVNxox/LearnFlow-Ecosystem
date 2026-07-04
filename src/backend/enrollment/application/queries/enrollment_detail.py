"""
EnrollmentDetail Query — Get enrollment details.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model

from src.backend.enrollment.domain.models import CourseEnrollment

User = get_user_model()


@dataclass
class EnrollmentDetailQuery:
    """Query to get enrollment details."""
    enrollment_id: UUID
    user_id: Optional[UUID] = None  


class EnrollmentDetailHandler:
    """Handler for EnrollmentDetail query."""

    @staticmethod
    def handle(query: EnrollmentDetailQuery) -> CourseEnrollment:
        """
        Get enrollment details.

        Raises:
            CourseEnrollment.DoesNotExist: If enrollment not found
            PermissionError: If user_id provided and doesn't match enrollment
        """
        enrollment = CourseEnrollment.objects.select_related('user').get(
            id=query.enrollment_id,
            deleted_at__isnull=True
        )

        
        if query.user_id and enrollment.user_id != query.user_id:
            raise PermissionError("You don't have permission to view this enrollment")

        return enrollment
