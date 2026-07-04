"""
Lesson List API — список уроков модуля.

Endpoint: GET /api/learning/{course_id}/modules/{module_id}/lessons/
Permissions: AllowAny (с проверкой видимости)
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.application.queries import CourseDetailQuery


class LessonListView(APIView):
    """
    GET /api/learning/{course_id}/modules/{module_id}/lessons/ — список уроков модуля.

    Path Parameters:
    - course_id: UUID курса
    - module_id: UUID модуля

    Visibility:
    - Unauthenticated: только published уроки в published модуле
    - Authenticated: published уроки
    - Staff/Author: все статусы включая drafts

    Response: List[Lesson]
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, course_id: str, module_id: str) -> Response:
        """Возвращает список уроков модуля."""

        user = request.user if request.user.is_authenticated else None

        course = CourseDetailQuery.get_course_detail(course_id=course_id, user=user)

        if not course:
            return Response(
                {"detail": "Course not found or not accessible."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        module = None
        for m in course.modules:
            if str(m.id) == module_id:
                module = m
                break

        if not module:
            return Response(
                {"detail": "Module not found in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        results = [
            {
                "id": lesson.id,
                "title": lesson.title,
                "description": lesson.description,
                "order": lesson.order,
                "estimated_minutes": lesson.estimated_minutes,
                "is_published": lesson.is_published,
                "is_free_preview": lesson.is_free_preview,
                "has_homework": lesson.has_homework,
                "has_quiz": lesson.has_quiz,
                "has_practice": lesson.has_practice,
            }
            for lesson in module.lessons
        ]

        return Response(results, status=status.HTTP_200_OK)
