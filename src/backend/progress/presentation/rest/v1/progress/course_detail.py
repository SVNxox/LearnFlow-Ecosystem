"""
GET /api/v1/progress/courses/{enrollment_id}/

Returns detailed progress for a specific course enrollment.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from src.backend.progress.domain.models import CourseProgress
from src.backend.progress.application.queries import GetCourseProgressDetailQuery


class CourseProgressDetailView(APIView):
    """
    Detailed progress for a course enrollment.

    Shows all modules and lessons with their status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, enrollment_id):
        """
        GET /api/v1/progress/courses/{enrollment_id}/

        Returns:
        {
            "enrollment_id": "uuid",
            "course_id": "uuid",
            "status": "in_progress",
            "completion_percentage": 75,
            "completed_lessons": 15,
            "total_lessons": 20,
            "started_at": "2026-06-01T10:00:00Z",
            "modules": [
                {
                    "module_id": "uuid",
                    "module_order": 1,
                    "status": "completed",
                    "completed_lessons": 5,
                    "total_lessons": 5,
                    "assessment_required": true,
                    "assessment_passed": true,
                    "lessons": [
                        {
                            "lesson_id": "uuid",
                            "lesson_order": 1,
                            "status": "completed",
                            "viewed_required_count": 3,
                            "required_content_count": 3,
                            "has_homework": false,
                            "homework_submitted": false,
                            "completed_at": "2026-06-02T15:00:00Z"
                        }
                    ]
                }
            ]
        }
        """
        
        progress = get_object_or_404(
            CourseProgress,
            enrollment_id=enrollment_id,
            user_id=request.user.id
        )

        query = GetCourseProgressDetailQuery(enrollment_id=enrollment_id)
        result = query.execute()

        return Response({
            'enrollment_id': str(result.enrollment_id),
            'course_id': str(result.course_id),
            'status': result.status,
            'completion_percentage': result.completion_percentage,
            'completed_lessons': result.completed_lessons,
            'total_lessons': result.total_lessons,
            'started_at': result.started_at.isoformat() if result.started_at else None,
            'completed_at': result.completed_at.isoformat() if result.completed_at else None,
            'modules': [
                {
                    'module_id': str(m.module_id),
                    'module_order': m.module_order,
                    'status': m.status,
                    'completed_lessons': m.completed_lessons,
                    'total_lessons': m.total_lessons,
                    'assessment_required': m.assessment_required,
                    'assessment_passed': m.assessment_passed,
                    'lessons': [
                        {
                            'lesson_id': str(l.lesson_id),
                            'lesson_order': l.lesson_order,
                            'status': l.status,
                            'viewed_required_count': l.viewed_required_count,
                            'required_content_count': l.required_content_count,
                            'has_homework': l.has_homework,
                            'homework_submitted': l.homework_submitted,
                            'completed_at': l.completed_at.isoformat() if l.completed_at else None,
                        }
                        for l in m.lessons
                    ]
                }
                for m in result.modules
            ]
        })
