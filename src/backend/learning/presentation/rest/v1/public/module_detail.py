"""
Public Module Detail API — просмотр модуля для студентов/менторов.

Endpoint: GET /api/learning/modules/{module_id}/
Permissions: AllowAny (только published)
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.application.queries.module_catalog import ModuleCatalogQuery


class PublicModuleDetailView(APIView):
    """
    GET /api/learning/modules/{module_id}/ — детали опубликованного модуля.

    Видит ТОЛЬКО published модули.
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, module_id: str) -> Response:
        module = ModuleCatalogQuery.get_published_module(module_id)

        if not module:
            return Response(
                {"detail": "Module not found or not published."},
                status=status.HTTP_404_NOT_FOUND,
            )

        lessons = ModuleCatalogQuery.get_published_lessons_for_module(module_id)

        response_data = {
            "id": str(module.id),
            "title": module.title,
            "description": module.description,
            "estimated_hours": module.estimated_hours,
            "order": module.order,
            "is_published": module.is_published,
            "course_id": str(module.course_id),
            "lessons": [
                {
                    "id": str(lesson.id),
                    "title": lesson.title,
                    "order": lesson.order,
                    "estimated_minutes": lesson.estimated_minutes,
                    "is_free_preview": lesson.is_free_preview,
                    "has_homework": getattr(lesson, 'has_homework', False),
                    "has_quiz": getattr(lesson, 'has_quiz', False),
                    "has_practice": getattr(lesson, 'has_practice', False),
                }
                for lesson in lessons
            ],
        }

        return Response(response_data, status=status.HTTP_200_OK)