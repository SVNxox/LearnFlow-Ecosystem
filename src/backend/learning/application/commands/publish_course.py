"""
PublishCourseCommand — публикация курса.

Business Rules:
- Курс должен быть в статусе 'draft'
- Минимум 1 опубликованный модуль с минимум 1 опубликованным уроком
- Slug становится immutable после публикации
- Emit CoursePublished event (для других доменов)

Permissions:
- Admin или Staff
- Course Author (автор курса)
"""

from django.contrib.auth import get_user_model
from django.db import transaction

from src.backend.core.exceptions import (
    AccessDeniedError,
    BusinessValidationError,
    NotFoundError,
)
from src.backend.learning.domain.models import Course

User = get_user_model()


def _check_course_permission(actor: User, course: Course) -> None:
    """
    Проверяет права на публикацию/снятие с публикации курса.

    Разрешено:
    - admin
    - staff
    - course author (создатель курса)

    Raises:
        AccessDeniedError: если нет прав
    """
    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = course.created_by_id == actor.id

    if not (is_admin or is_staff or is_course_author):
        raise AccessDeniedError(
            "Only admin, staff, or course author can publish/unpublish courses",
            code="insufficient_permissions",
        )


class PublishCourseCommand:
    """
    Command для публикации курса.

    Permissions: Admin, Staff, or Course Author
    """

    @staticmethod
    @transaction.atomic
    def execute(course_id: str, actor: User) -> Course:
        """
        Публикует курс (draft → published).

        Проверяет:
        1. Курс существует и не удалён
        2. Actor имеет право публиковать (admin/staff/created_by)
        3. Курс в статусе 'draft'
        4. Есть минимум 1 опубликованный модуль
        5. В каждом опубликованном модуле есть минимум 1 опубликованный урок

        Args:
            course_id: UUID курса
            actor: Пользователь публикующий курс

        Returns:
            Course instance (status='published')

        Raises:
            NotFoundError: если курс не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если курс не готов к публикации
        """
        
        try:
            course = Course.objects.select_for_update().get(
                id=course_id, deleted_at__isnull=True
            )
        except Course.DoesNotExist:
            raise NotFoundError(
                f"Course {course_id} not found",
                code="course_not_found",
            )

        
        _check_course_permission(actor, course)

        
        if course.status != "draft":
            raise BusinessValidationError(
                code="invalid_status_for_publish",
                lang="uz",
                message=(
                    f"Cannot publish course with status '{course.status}'. "
                    "Only draft courses can be published."
                ),
            )

        
        published_modules = course.modules.filter(
            is_published=True, deleted_at__isnull=True
        )

        if not published_modules.exists():
            raise BusinessValidationError(
                code="no_published_modules",
                lang="uz",
                message=(
                    "Cannot publish course: no published modules found. "
                    "Create and publish at least one module with lessons."
                ),
            )

        
        for module in published_modules:
            published_lessons = module.lessons.filter(
                is_published=True, deleted_at__isnull=True
            )
            if not published_lessons.exists():
                raise BusinessValidationError(
                    code="module_has_no_published_lessons",
                    lang="uz",
                    message=(
                        f"Cannot publish course: module '{module.title}' has no published lessons. "
                        f"Publish at least one lesson in this module."
                    ),
                )

        
        course.status = "published"
        course.save(update_fields=["status", "updated_at"])

        
        

        return course

    @staticmethod
    @transaction.atomic
    def unpublish_course(course_id: str, actor: User) -> Course:
        """
        Снимает курс с публикации (published → draft).

        Args:
            course_id: UUID курса
            actor: Пользователь (admin/staff/author)

        Returns:
            Course instance (status='draft')

        Raises:
            NotFoundError: если курс не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если курс нельзя снять с публикации
        """
        try:
            course = Course.objects.select_for_update().get(
                id=course_id, deleted_at__isnull=True
            )
        except Course.DoesNotExist:
            raise NotFoundError(
                f"Course {course_id} not found",
                code="course_not_found",
            )

        
        _check_course_permission(actor, course)

        
        if course.status != "published":
            raise BusinessValidationError(
                code="invalid_status_for_unpublish",
                lang="uz",
                message=(
                    f"Cannot unpublish course with status '{course.status}'. "
                    "Only published courses can be unpublished."
                ),
            )

        
        from src.backend.enrollment.domain.models import CourseEnrollment

        active_enrollments_count = CourseEnrollment.objects.filter(
            course_id=course.id,
            status="active",
            deleted_at__isnull=True,
        ).count()

        if active_enrollments_count > 0:
            raise BusinessValidationError(
                code="active_enrollments_exist",
                lang="uz",
                message=(
                    f"Cannot unpublish course: {active_enrollments_count} active enrollments exist. "
                    "Drop or complete all enrollments first, or archive the course instead."
                ),
            )

        
        course.status = "draft"
        course.save(update_fields=["status", "updated_at"])

        
        

        return course