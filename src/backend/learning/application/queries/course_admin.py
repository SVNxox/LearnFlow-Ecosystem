"""
CourseAdminQuery — админские запросы для управления курсами.

Возвращает курсы ЛЮБОГО статуса (draft, published, archived).
Используется ТОЛЬКО в admin endpoints.
"""

from typing import Optional
from django.db.models import Q, QuerySet

from src.backend.learning.domain.models import Course


class CourseAdminQuery:
    """Read-only queries для админского управления курсами."""

    @staticmethod
    def get_all_courses(
        status_filter: Optional[str] = None,
        category_slug: Optional[str] = None,
        delivery_format: Optional[str] = None,
        language: Optional[str] = None,
    ) -> QuerySet[Course]:
        """
        Возвращает все курсы с фильтрами (включая draft, archived).

        Args:
            status_filter: 'draft' | 'published' | 'archived' | 'all' | None (все)
            category_slug: Фильтр по категории
            delivery_format: 'online' | 'offline'
            language: BCP-47 код языка
        """
        if status_filter is None or status_filter == 'all':
            allowed_statuses = ['draft', 'published', 'archived']
        elif status_filter in ['draft', 'published', 'archived']:
            allowed_statuses = [status_filter]
        else:
            return Course.objects.none()

        qs = (
            Course.objects.filter(
                status__in=allowed_statuses,
                deleted_at__isnull=True
            )
            .select_related("category")
            .order_by("-created_at")
        )

        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        if delivery_format == "online":
            qs = qs.filter(supports_online=True)
        elif delivery_format == "offline":
            qs = qs.filter(supports_offline=True)

        if language:
            qs = qs.filter(language=language)

        return qs

    @staticmethod
    def get_course_by_id(course_id: str) -> Optional[Course]:
        """
        Возвращает курс по ID (любой статус).

        Args:
            course_id: UUID курса
        """
        try:
            return Course.objects.select_related('category').get(
                id=course_id,
                deleted_at__isnull=True
            )
        except (Course.DoesNotExist, ValueError, TypeError):
            return None

    @staticmethod
    def search_courses(
        query: str,
        status_filter: Optional[str] = None,
        language: Optional[str] = None,
    ) -> QuerySet[Course]:
        """Поиск по всем курсам (включая draft, archived)."""
        if not query or not query.strip():
            return Course.objects.none()

        search_term = query.strip()

        if status_filter is None or status_filter == 'all':
            allowed_statuses = ['draft', 'published', 'archived']
        elif status_filter in ['draft', 'published', 'archived']:
            allowed_statuses = [status_filter]
        else:
            return Course.objects.none()

        qs = (
            Course.objects.filter(
                status__in=allowed_statuses,
                deleted_at__isnull=True
            )
            .filter(
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(short_description__icontains=search_term) |
                Q(category__name__icontains=search_term)
            )
            .select_related("category")
            .order_by("-created_at")
        )

        if language:
            qs = qs.filter(language=language)

        return qs