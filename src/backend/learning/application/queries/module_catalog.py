"""
ModuleCatalogQuery — публичные запросы для просмотра модулей.

Visibility: Только published модули для student, mentor, anonymous.
"""

from typing import Optional
from django.db.models import QuerySet

from src.backend.learning.domain.models import Module, Lesson


class ModuleCatalogQuery:
    """
    Read-only queries для публичного просмотра модулей.
    Возвращает ТОЛЬКО published модули.
    """

    @staticmethod
    def get_published_modules_for_course(course_id: str) -> QuerySet[Module]:
        """
        Возвращает опубликованные модули курса.
        """
        return (
            Module.objects.filter(
                course_id=course_id,
                is_published=True,
                deleted_at__isnull=True
            )
            .prefetch_related("lessons")
            .order_by("order")
        )

    @staticmethod
    def get_published_module(module_id: str) -> Optional[Module]:
        """
        Возвращает опубликованный модуль по ID.
        """
        try:
            return Module.objects.get(
                id=module_id,
                is_published=True,
                deleted_at__isnull=True
            )
        except Module.DoesNotExist:
            return None

    @staticmethod
    def get_published_lessons_for_module(module_id: str) -> QuerySet[Lesson]:
        """
        Возвращает опубликованные уроки модуля.
        """
        return (
            Lesson.objects.filter(
                module_id=module_id,
                is_published=True,
                deleted_at__isnull=True
            )
            .order_by("order")
        )