"""
Admin Course Detail API — детальная информация о курсе для админки.

Endpoint: GET /api/v1/learning/admin/courses/{course_id}/
Permissions: Только admin/staff
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.application.queries.course_admin import CourseAdminQuery


class AdminCourseDetailView(APIView):
    """
    GET /api/v1/learning/admin/courses/{course_id}/ — детали курса для админки.
    Видит курсы ЛЮБОГО статуса (draft, published, archived).
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, course_id: str) -> Response:
        course = CourseAdminQuery.get_course_by_id(course_id)

        if not course:
            return Response(
                {"detail": "Course not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        
        from src.backend.enrollment.models import CourseEnrollment
        active_enrollment_count = CourseEnrollment.objects.filter(
            course_id=course.id,
            status='active',
            deleted_at__isnull=True
        ).count()

        
        from src.backend.learning.domain.models import Module, Lesson

        modules_data = []
        modules = (
            Module.objects.filter(course=course, deleted_at__isnull=True)
            .order_by('order')
        )

        for module in modules:
            lessons = (
                Lesson.objects.filter(module=module, deleted_at__isnull=True)
                .order_by('order')
            )

            lessons_data = [
                {
                    "id": str(lesson.id),
                    "title": lesson.title,
                    "order": lesson.order,
                    "estimated_minutes": getattr(lesson, 'estimated_minutes', 0),
                    "is_published": getattr(lesson, 'is_published', False),
                    "is_free_preview": getattr(lesson, 'is_free_preview', False),
                    "has_homework": getattr(lesson, 'has_homework', False),
                    "has_quiz": getattr(lesson, 'has_quiz', False),
                    "has_practice": getattr(lesson, 'has_practice', False),
                }
                for lesson in lessons
            ]

            modules_data.append({
                "id": str(module.id),
                "title": module.title,
                "description": module.description,
                "order": module.order,
                "estimated_hours": getattr(module, 'estimated_hours', 0),
                "is_published": getattr(module, 'is_published', False),
                "lesson_count": len(lessons_data),
                "lessons": lessons_data,
            })

        response_data = {
            "id": str(course.id),
            "title": course.title,
            "slug": course.slug,
            "description": course.description,
            "short_description": course.short_description,
            "thumbnail_url": course.thumbnail_url,
            "category": {
                "name": course.category.name,
                "slug": course.category.slug,
            } if course.category else None,
            "status": course.status,
            "supports_online": course.supports_online,
            "supports_offline": course.supports_offline,
            "language": course.language,
            "estimated_weeks": course.estimated_weeks,
            "is_sequential": getattr(course, 'is_sequential', False),
            "active_enrollment_count": active_enrollment_count,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            
            "price": str(getattr(course, 'price', '0') or '0'),
            "currency": getattr(course, 'currency', 'UZS') or 'UZS',
            "modules": modules_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)