"""
CourseCatalogQuery — публичные запросы для каталога курсов.

Responsibilities:
- Список опубликованных курсов с фильтрами
- Поиск по курсам
- Данные для карточек курсов
- Список категорий

Visibility: Публичные endpoints (не требуют аутентификации)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count, Q, QuerySet

from src.backend.learning.domain.models import Course, CourseCategory


@dataclass
class CourseCardDTO:
    """Lightweight DTO для каталожной карточки курса."""

    id: str
    title: str
    slug: str
    short_description: Optional[str]
    thumbnail_url: Optional[str]
    category_name: Optional[str]
    estimated_weeks: Optional[int]
    active_enrollment_count: int
    supports_online: bool
    supports_offline: bool


@dataclass
class CategoryDTO:
    """DTO для категории с количеством курсов."""

    id: str
    name: str
    slug: str
    parent_id: Optional[str]
    course_count: int
    order: int


class CourseCatalogQuery:
    """
    Read-only queries для публичного каталога курсов.

    Все методы возвращают только опубликованные (status='published') курсы.
    """

    @staticmethod
    def get_published_courses(
        category_slug: Optional[str] = None,
        delivery_format: Optional[str] = None,  
        language: Optional[str] = None,
    ) -> QuerySet[Course]:
        """
        Возвращает опубликованные курсы с фильтрами.

        Args:
            category_slug: Фильтр по категории (slug)
            delivery_format: Фильтр по формату ('online' | 'offline')
            language: Фильтр по языку (BCP-47 код)

        Returns:
            QuerySet[Course] с select_related для категории
        """
        qs = (
            Course.objects.filter(status="published", deleted_at__isnull=True)
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
    def get_course_card(slug: str) -> Optional[CourseCardDTO]:
        """
        Возвращает данные для одной карточки курса (lightweight).

        Args:
            slug: URL-safe идентификатор курса

        Returns:
            CourseCardDTO или None если курс не найден/не опубликован
        """
        try:
            course = (
                Course.objects.filter(
                    slug=slug, status="published", deleted_at__isnull=True
                )
                .select_related("category")
                .get()
            )

            
            from src.backend.enrollment.models import CourseEnrollment
            active_enrollment_count = CourseEnrollment.objects.filter(
                course_id=course.id,
                status='active',
                deleted_at__isnull=True
            ).count()

            return CourseCardDTO(
                id=str(course.id),
                title=course.title,
                slug=course.slug,
                short_description=course.short_description,
                thumbnail_url=course.thumbnail_url,
                category_name=course.category.name if course.category else None,
                estimated_weeks=course.estimated_weeks,
                active_enrollment_count=active_enrollment_count,
                supports_online=course.supports_online,
                supports_offline=course.supports_offline,
            )
        except Course.DoesNotExist:
            return None

    @staticmethod
    def get_all_categories() -> list[CategoryDTO]:
        """
        Возвращает все активные категории с количеством опубликованных курсов.

        Returns:
            List[CategoryDTO] упорядоченный по order
        """
        categories = (
            CourseCategory.objects.filter(is_active=True)
            .annotate(
                course_count=Count(
                    "learning",
                    filter=Q(
                        courses__status="published", courses__deleted_at__isnull=True
                    ),
                )
            )
            .order_by("order", "name")
        )

        return [
            CategoryDTO(
                id=str(cat.id),
                name=cat.name,
                slug=cat.slug,
                parent_id=str(cat.parent_id) if cat.parent_id else None,
                course_count=cat.course_count,
                order=cat.order,
            )
            for cat in categories
        ]

    @staticmethod
    def search_courses(query: str, language: Optional[str] = None) -> QuerySet[Course]:
        """
        Поиск по опубликованным курсам (title + description + category).

        Использует icontains для поиска по подстрокам (как в users).

        Args:
            query: Поисковый запрос
            language: Фильтр по языку (опционально)

        Returns:
            QuerySet[Course] упорядоченный по дате создания
        """
        if not query or not query.strip():
            return Course.objects.none()

        search_term = query.strip()

        
        qs = (
            Course.objects.filter(status="published", deleted_at__isnull=True)
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
