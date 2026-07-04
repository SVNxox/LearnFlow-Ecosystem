"""
Module List API — список модулей курса.

Endpoint: GET /api/learning/{course_id}/modules/
Permissions: AllowAny (с проверкой видимости)
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.application.queries import CourseDetailQuery


class ModuleListView(APIView):
    """
    GET /api/learning/{course_id}/modules/ — список модулей курса.

    Path Parameters:
    - course_id: UUID курса

    Query Parameters:
    - include_lessons: bool (default true) - включать ли уроки в ответ

    Visibility:
    - Unauthenticated: только published модули в published курсе
    - Authenticated: published модули
    - Staff/Author: все статусы включая drafts

    Response: List[Module]
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, course_id: str) -> Response:
        """Возвращает список модулей курса."""

        user = request.user if request.user.is_authenticated else None

        course = CourseDetailQuery.get_course_detail(course_id=course_id, user=user)

        if not course:
            return Response(
                {"detail": "Course not found or not accessible."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        include_lessons = request.query_params.get("include_lessons", "true").lower() == "true"

        results = [
            {
                "id": module.id,
                "title": module.title,
                "description": module.description,
                "order": module.order,
                "estimated_hours": module.estimated_hours,
                "is_published": module.is_published,
                "lesson_count": module.lesson_count,
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "order": lesson.order,
                        "estimated_minutes": lesson.estimated_minutes,
                        "is_published": lesson.is_published,
                        "is_free_preview": lesson.is_free_preview,
                        "has_homework": lesson.has_homework,
                        "has_quiz": lesson.has_quiz,
                        "has_practice": lesson.has_practice,
                    }
                    for lesson in module.lessons
                ] if include_lessons else [],
            }
            for module in course.modules
        ]

        return Response(results, status=status.HTTP_200_OK)
