"""
Course Detail API — детальная информация о курсе.

Endpoint: GET /api/learning/{slug}/
Permissions: AllowAny (публичный endpoint с visibility rules)
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.application.queries import CourseDetailQuery


class CourseDetailView(APIView):
    """
    GET /api/learning/{slug}/ — детальная информация о курсе.

    Path Parameters:
    - slug: URL-safe идентификатор курса

    Visibility:
    - Unauthenticated: только published курс
    - Authenticated: published курс
    - Staff/Author: все статусы включая drafts

    Response: CourseDetail with modules and lessons
    """

    permission_classes = [AllowAny]

    def get(self, request: Request, slug: str) -> Response:
        """Возвращает детальную информацию о курсе."""

        user = request.user if request.user.is_authenticated else None

        course = CourseDetailQuery.get_course_by_slug(slug=slug, user=user)

        if not course:
            return Response(
                {"detail": "Course not found or not accessible."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        response_data = {
            "id": course.id,
            "title": course.title,
            "slug": course.slug,
            "description": course.description,
            "short_description": course.short_description,
            "thumbnail_url": course.thumbnail_url,
            "category_name": course.category_name,
            "status": course.status,
            "supports_online": course.supports_online,
            "supports_offline": course.supports_offline,
            "language": course.language,
            "estimated_weeks": course.estimated_weeks,
            "is_sequential": course.is_sequential,
            "active_enrollment_count": course.active_enrollment_count,
            "created_by_name": course.created_by_name,
            "price": str(course.price),
            "currency": course.currency,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "modules": [
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
                    ],
                }
                for module in course.modules
            ],
        }

        return Response(response_data, status=status.HTTP_200_OK)



