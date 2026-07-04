"""
CourseDetailQuery — детальные запросы для курсов с visibility rules.

Responsibilities:
- Полная информация о курсе с модулями и уроками
- Visibility-aware filtering (публичные, студент, автор)
- Данные для страницы курса
- Проверка доступа к черновикам

Visibility Rules:
- Unauthenticated: только published курсы
- Student (enrolled): только published контент
- Admin/Staff/Course Author: все статусы включая drafts
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q, QuerySet

from src.backend.learning.domain.models import Course, Lesson, Module

User = get_user_model()


@dataclass
class LessonMetadataDTO:
    """Metadata урока для curriculum."""

    id: str
    title: str
    order: int
    estimated_minutes: Optional[int]
    is_published: bool
    is_free_preview: bool
    has_homework: bool
    has_quiz: bool
    has_practice: bool


@dataclass
class ModuleDTO:
    """Module с metadata уроков."""

    id: str
    title: str
    description: Optional[str]
    order: int
    estimated_hours: Optional[int]
    is_published: bool
    lesson_count: int
    lessons: list[LessonMetadataDTO]


@dataclass
class CourseDetailDTO:
    """Полная информация о курсе для страницы курса."""

    id: str
    title: str
    slug: str
    description: Optional[str]
    short_description: Optional[str]
    thumbnail_url: Optional[str]
    category_name: Optional[str]
    status: str
    supports_online: bool
    supports_offline: bool
    language: str
    estimated_weeks: Optional[int]
    is_sequential: bool
    active_enrollment_count: int
    modules: list[ModuleDTO]
    created_by_name: str
    created_at: str
    updated_at: str
    price: str  
    currency: str


def _can_view_all_content(user: Optional[User], course: Optional[Course] = None) -> bool:
    """
    Проверяет, может ли пользователь видеть весь контент (включая drafts).

    Разрешено:
    - admin
    - staff
    - course author (если передан course)

    Запрещено:
    - mentor, student, anonymous
    """
    if not user or not user.is_authenticated:
        return False

    
    user_roles = []
    if hasattr(user, 'get_roles'):
        try:
            user_roles = user.get_roles()
        except Exception:
            user_roles = []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = course and course.created_by_id == user.id

    return is_admin or is_staff or bool(is_course_author)


class CourseDetailQuery:
    """
    Read-only queries для детального просмотра курсов.
    Применяет visibility rules в зависимости от роли пользователя.
    """

    @staticmethod
    def get_course_detail(
            course_id: str, user: Optional[User] = None
    ) -> Optional[CourseDetailDTO]:
        """
        Возвращает полную информацию о курсе с модулями и уроками.
        """
        
        qs = Course.objects.filter(id=course_id, deleted_at__isnull=True).select_related(
            "category", "created_by"
        )

        try:
            course = qs.get()
        except Course.DoesNotExist:
            return None

        
        can_view_all = _can_view_all_content(user, course)

        
        if not can_view_all:
            if course.status != "published":
                return None

        
        from src.backend.enrollment.models import CourseEnrollment
        active_enrollment_count = CourseEnrollment.objects.filter(
            course_id=course.id,
            status='active',
            deleted_at__isnull=True
        ).count()

        
        modules = CourseDetailQuery._get_modules_for_course(
            course_id=course_id, user=user, can_view_all=can_view_all
        )

        
        created_by_name = "Unknown"
        if course.created_by:
            if hasattr(course.created_by, 'info') and course.created_by.info:
                first_name = course.created_by.info.first_name or ''
                last_name = course.created_by.info.last_name or ''
                full_name = f"{first_name} {last_name}".strip()
                if full_name:
                    created_by_name = full_name
                else:
                    created_by_name = course.created_by.email or "Unknown"
            else:
                created_by_name = course.created_by.email or "Unknown"

        return CourseDetailDTO(
            id=str(course.id),
            title=course.title,
            slug=course.slug,
            description=course.description,
            short_description=course.short_description,
            thumbnail_url=course.thumbnail_url,
            category_name=course.category.name if course.category else None,
            status=course.status,
            supports_online=course.supports_online,
            supports_offline=course.supports_offline,
            language=course.language,
            estimated_weeks=course.estimated_weeks,
            is_sequential=course.is_sequential,
            active_enrollment_count=active_enrollment_count,
            modules=modules,
            created_by_name=created_by_name,
            created_at=course.created_at.isoformat(),
            updated_at=course.updated_at.isoformat(),
            
            price=str(course.price),
            currency=course.currency or 'UZS',
        )

    @staticmethod
    def get_course_by_slug(
        slug: str, user: Optional[User] = None
    ) -> Optional[CourseDetailDTO]:
        """
        Возвращает курс по slug с теми же visibility rules.

        Args:
            slug: URL-safe идентификатор
            user: Текущий пользователь

        Returns:
            CourseDetailDTO или None
        """
        try:
            course = Course.objects.filter(
                slug=slug, deleted_at__isnull=True
            ).get()
            return CourseDetailQuery.get_course_detail(
                course_id=str(course.id), user=user
            )
        except Course.DoesNotExist:
            return None

    @staticmethod
    def get_course_for_author(
            course_id: str, user: User
    ) -> Optional[CourseDetailDTO]:
        """
        Возвращает курс для автора/staff — включая все drafts.
        """
        try:
            course = Course.objects.filter(
                id=course_id, deleted_at__isnull=True
            ).select_related("category", "created_by").get()

            
            if not _can_view_all_content(user, course):
                return None

            
            modules = CourseDetailQuery._get_modules_for_course(
                course_id=course_id, user=user, can_view_all=True
            )

            
            from src.backend.enrollment.models import CourseEnrollment
            active_enrollment_count = CourseEnrollment.objects.filter(
                course_id=course.id,
                status='active',
                deleted_at__isnull=True
            ).count()

            
            created_by_name = "Unknown"
            if course.created_by:
                if hasattr(course.created_by, 'info') and course.created_by.info:
                    first_name = course.created_by.info.first_name or ''
                    last_name = course.created_by.info.last_name or ''
                    full_name = f"{first_name} {last_name}".strip()
                    if full_name:
                        created_by_name = full_name
                    else:
                        created_by_name = course.created_by.email or "Unknown"
                else:
                    created_by_name = course.created_by.email or "Unknown"

            return CourseDetailDTO(
                id=str(course.id),
                title=course.title,
                slug=course.slug,
                description=course.description,
                short_description=course.short_description,
                thumbnail_url=course.thumbnail_url,
                category_name=course.category.name if course.category else None,
                status=course.status,
                supports_online=course.supports_online,
                supports_offline=course.supports_offline,
                language=course.language,
                estimated_weeks=course.estimated_weeks,
                is_sequential=course.is_sequential,
                active_enrollment_count=active_enrollment_count,
                modules=modules,
                created_by_name=created_by_name,
                created_at=course.created_at.isoformat(),
                updated_at=course.updated_at.isoformat(),
                
                price=str(course.price),
                currency=course.currency or 'UZS',
            )
        except Course.DoesNotExist:
            return None

    @staticmethod
    def _get_modules_for_course(
        course_id: str, user: Optional[User], can_view_all: bool
    ) -> list[ModuleDTO]:
        """
        Internal: загружает модули с уроками с учётом visibility.

        Args:
            course_id: UUID курса
            user: Текущий пользователь
            can_view_all: Флаг — может ли видеть весь контент (admin/staff/author)

        Returns:
            List[ModuleDTO] упорядоченный по order
        """
        
        module_qs = Module.objects.filter(
            course_id=course_id, deleted_at__isnull=True
        )

        
        if not can_view_all:
            module_qs = module_qs.filter(is_published=True)

        
        lesson_qs = Lesson.objects.filter(deleted_at__isnull=True).select_related(
            "homework", "quiz"
        )

        
        if not can_view_all:
            lesson_qs = lesson_qs.filter(is_published=True)

        
        modules = module_qs.prefetch_related(
            Prefetch("lessons", queryset=lesson_qs.order_by("order"))
        ).order_by("order")

        result = []
        for module in modules:
            lessons_data = [
                LessonMetadataDTO(
                    id=str(lesson.id),
                    title=lesson.title,
                    order=lesson.order,
                    estimated_minutes=lesson.estimated_minutes,
                    is_published=lesson.is_published,
                    is_free_preview=lesson.is_free_preview,
                    has_homework=hasattr(lesson, "homework") and lesson.homework is not None,
                    has_quiz=hasattr(lesson, "quiz") and lesson.quiz is not None,
                    has_practice=lesson.practice_items.exists()
                    if hasattr(lesson, "practice_items")
                    else False,
                )
                for lesson in module.lessons.all()
            ]

            result.append(
                ModuleDTO(
                    id=str(module.id),
                    title=module.title,
                    description=module.description,
                    order=module.order,
                    estimated_hours=module.estimated_hours,
                    is_published=module.is_published,
                    lesson_count=len(lessons_data),
                    lessons=lessons_data,
                )
            )

        return result