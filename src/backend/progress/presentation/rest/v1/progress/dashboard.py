"""
GET /api/v1/progress/me/

Returns student's progress dashboard across all enrolled courses.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from src.backend.progress.application.queries import GetProgressDashboardQuery, GetProgressDashboardHandler


class MyProgressDashboardView(APIView):
    """
    Student's progress dashboard.

    Shows all enrolled courses with completion percentage and status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET /api/v1/progress/me/

        Returns:
        {
            "courses": [
                {
                    "enrollment_id": "uuid",
                    "course_id": "uuid",
                    "course_title": "str",
                    "status": "in_progress|completed",
                    "completion_percentage": 75,
                    "completed_lessons": 15,
                    "total_lessons": 20,
                    "started_at": "2026-06-01T10:00:00Z",
                    "completed_at": null,
                    "last_activity_at": "2026-06-09T12:30:00Z"
                }
            ]
        }
        """
        query = GetProgressDashboardQuery(user_id=request.user.id)
        result = GetProgressDashboardHandler.handle(query)

        return Response({
            'courses': [
                {
                    'enrollment_id': str(c.enrollment_id),
                    'course_id': str(c.course_id),
                    'course_title': c.course_title,
                    'status': c.status,
                    'completion_percentage': c.completion_percentage,
                    'completed_lessons': c.completed_lessons,
                    'total_lessons': c.total_lessons,
                    'enrolled_at': c.enrolled_at.isoformat() if c.enrolled_at else None,
                    'completed_at': c.completed_at.isoformat() if c.completed_at else None,
                    'last_activity_at': c.last_activity_at.isoformat() if c.last_activity_at else None,
                }
                for c in result.courses
            ]
        })
