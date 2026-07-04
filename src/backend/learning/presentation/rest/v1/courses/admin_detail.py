"""
Course Admin Detail API — админские операции с курсом.

Endpoints:
- GET    /api/v1/learning/admin/courses/{id}/ — детали курса
- PATCH  /api/v1/learning/admin/courses/{id}/ — обновление
- DELETE /api/v1/learning/admin/courses/{id}/ — удаление (soft delete)

Permissions: IsAuthenticated + IsAdminOrStaff (или автор курса для PATCH/DELETE)
"""

import logging
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from src.backend.learning.utils.permissions import IsAdminOrStaff
from src.backend.learning.domain.models import Course, Module, Lesson
from src.backend.core.exceptions import BusinessValidationError

logger = logging.getLogger(__name__)


class CourseAdminDetailView(APIView):
    """
    GET + PATCH + DELETE для курса по ID.
    """

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def get(self, request: Request, course_id: str) -> Response:
        """Возвращает детали курса для редактирования."""
        course = get_object_or_404(Course, id=course_id, deleted_at__isnull=True)

        
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
                    "description": getattr(lesson, 'description', '') or '',
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
                "description": module.description or '',
                "order": module.order,
                "estimated_hours": getattr(module, 'estimated_hours', 0),
                "is_published": getattr(module, 'is_published', False),
                "lesson_count": len(lessons_data),
                "lessons": lessons_data,
            })

        
        from src.backend.enrollment.models import CourseEnrollment
        active_enrollment_count = CourseEnrollment.objects.filter(
            course_id=course.id,
            status='active',
            deleted_at__isnull=True
        ).count()

        return Response({
            "id": str(course.id),
            "title": course.title,
            "slug": course.slug,
            "description": course.description or "",
            "short_description": course.short_description or "",
            "thumbnail_url": course.thumbnail_url or "",
            
            "category": {
                "id": str(course.category.id),
                "name": course.category.name,
                "slug": course.category.slug,
            } if course.category else None,
            "category_id": str(course.category_id) if course.category_id else None,
            "status": course.status,
            "supports_online": course.supports_online,
            "supports_offline": course.supports_offline,
            "language": course.language,
            "estimated_weeks": course.estimated_weeks,
            "is_sequential": course.is_sequential,
            "created_by_id": str(course.created_by_id),
            "created_at": course.created_at.isoformat(),
            "updated_at": course.updated_at.isoformat(),
            "active_enrollment_count": active_enrollment_count,
            
            "price": str(course.price) if course.price is not None else "0",
            "currency": course.currency or "UZS",
            
            "modules": modules_data,
        }, status=status.HTTP_200_OK)

    def patch(self, request: Request, course_id: str) -> Response:
        """Обновляет курс."""
        course = get_object_or_404(Course, id=course_id, deleted_at__isnull=True)

        data = request.data
        update_fields = []

        
        if "title" in data:
            clean_title = data["title"].strip()
            if len(clean_title) < 3:
                return Response(
                    {"error": "title_too_short", "detail": "Kurs nomi kamida 3 ta belgidan iborat bo'lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            course.title = clean_title
            update_fields.append("title")

        if "slug" in data:
            course.slug = data["slug"]
            update_fields.append("slug")

        if "description" in data:
            course.description = data["description"]
            update_fields.append("description")

        if "short_description" in data:
            course.short_description = data["short_description"]
            update_fields.append("short_description")

        if "thumbnail_url" in data:
            course.thumbnail_url = data["thumbnail_url"]
            update_fields.append("thumbnail_url")

        if "category_id" in data:
            course.category_id = data["category_id"]
            update_fields.append("category_id")

        if "status" in data:
            course.status = data["status"]
            update_fields.append("status")

        if "supports_online" in data:
            course.supports_online = data["supports_online"]
            update_fields.append("supports_online")

        if "supports_offline" in data:
            course.supports_offline = data["supports_offline"]
            update_fields.append("supports_offline")

        
        if not course.supports_online and not course.supports_offline:
            return Response(
                {"error": "delivery_format_required", "detail": "Kurs kamida bitta formatni qo'llab-quvvatlashi kerak"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if "language" in data:
            course.language = data["language"]
            update_fields.append("language")

        if "estimated_weeks" in data:
            weeks = data["estimated_weeks"]
            if weeks is not None and weeks <= 0:
                return Response(
                    {"error": "invalid_estimated_weeks", "detail": "Taxminiy haftalar 0 dan katta bo'lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            course.estimated_weeks = weeks
            update_fields.append("estimated_weeks")

        if "is_sequential" in data:
            course.is_sequential = data["is_sequential"]
            update_fields.append("is_sequential")

        
        if "price" in data:
            try:
                price_value = Decimal(str(data["price"]))
                if price_value < 0:
                    return Response(
                        {"error": "invalid_price", "detail": "Narx manfiy bo'lishi mumkin emas"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                course.price = price_value
                update_fields.append("price")
            except (InvalidOperation, ValueError, TypeError):
                return Response(
                    {"error": "invalid_price", "detail": "Narx formati noto'g'ri"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if "currency" in data:
            currency = data["currency"]
            if currency not in ['UZS', 'USD']:
                return Response(
                    {"error": "invalid_currency", "detail": "Valyuta UZS yoki USD bo'lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            course.currency = currency
            update_fields.append("currency")

        if update_fields:
            update_fields.append("updated_at")
            course.save(update_fields=update_fields)

        return Response({
            "id": str(course.id),
            "title": course.title,
            "slug": course.slug,
            "status": course.status,
            "price": str(course.price),
            "currency": course.currency,
            "updated_at": course.updated_at.isoformat(),
        }, status=status.HTTP_200_OK)

    def delete(self, request: Request, course_id: str) -> Response:
        """Удаляет курс (soft delete)."""
        course = get_object_or_404(Course, id=course_id, deleted_at__isnull=True)

        
        from src.backend.enrollment.models import CourseEnrollment
        enrollment_count = CourseEnrollment.objects.filter(
            course_id=course.id,
            deleted_at__isnull=True,
        ).count()

        if enrollment_count > 0:
            return Response(
                {
                    "error": "enrollments_exist",
                    "detail": f"Kursni o'chirib bo'lmaydi: {enrollment_count} ta yozilgan talaba bor. Arxivlang.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        
        course.deleted_at = timezone.now()
        course.save(update_fields=["deleted_at"])

        return Response(
            {"detail": "Course deleted successfully"},
            status=status.HTTP_200_OK
        )