"""
Admin enrollments query — list all enrollments with filters.

Admin-only endpoint to view all enrollments across the platform.
"""

from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

from src.backend.enrollment.domain.models import CourseEnrollment


@dataclass
class AdminEnrollmentsQuery:
    """Query to list all enrollments (admin only)."""
    course_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20


class AdminEnrollmentsHandler:
    """Handler for admin enrollments query."""

    @staticmethod
    def handle(query: AdminEnrollmentsQuery) -> dict:
        """
        Execute admin enrollments query.

        Returns paginated enrollments with filters.
        """
        queryset = CourseEnrollment.objects.select_related('user', 'user__info').all()

        
        if query.course_id:
            queryset = queryset.filter(course_id=query.course_id)

        if query.student_id:
            queryset = queryset.filter(user_id=query.student_id)

        if query.status:
            queryset = queryset.filter(status=query.status)

        
        queryset = queryset.order_by('-enrolled_at')

        
        total = queryset.count()
        offset = (query.page - 1) * query.page_size
        limit = query.page_size

        enrollments = list(queryset[offset:offset + limit])

        return {
            'results': enrollments,
            'count': total,
            'page': query.page,
            'page_size': query.page_size,
            'total_pages': (total + query.page_size - 1) // query.page_size,
        }
