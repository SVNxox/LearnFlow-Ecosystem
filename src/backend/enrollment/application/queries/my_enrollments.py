"""
MyEnrollments Query — List user's enrollments.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from src.backend.enrollment.domain.models import CourseEnrollment

User = get_user_model()


@dataclass
class MyEnrollmentsQuery:
    """Query to list user's enrollments."""
    user_id: UUID
    status: Optional[str] = None


class MyEnrollmentsHandler:
    """Handler for MyEnrollments query."""

    @staticmethod
    def handle(query: MyEnrollmentsQuery) -> QuerySet[CourseEnrollment]:
        """
        Get user's enrollments.

        Returns:
            QuerySet of CourseEnrollment ordered by enrolled_at DESC
        """
        filters = {
            'user_id': query.user_id,
            'deleted_at__isnull': True
        }

        if query.status:
            filters['status'] = query.status

        enrollments = CourseEnrollment.objects.filter(
            **filters
        ).select_related('user').order_by('-enrolled_at')

        return enrollments
