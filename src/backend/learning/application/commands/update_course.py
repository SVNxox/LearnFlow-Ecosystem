"""
UpdateCourseCommand — обновление метаданных курса.

Business Rules:
- Slug immutable после публикации
- Нельзя убрать supports_offline если есть активные offline enrollments
- Нельзя удалить курс если есть любые enrollments (use archive instead)

Permissions:
- Admin или Staff
- Course Author (автор курса)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from src.backend.core.exceptions import (
    AccessDeniedError,
    BusinessValidationError,
    NotFoundError,
)
from src.backend.learning.domain.models import Course

User = get_user_model()


@dataclass
class UpdateCourseData:
    """Input data для обновления курса."""

    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category_id: Optional[str] = None
    supports_online: Optional[bool] = None
    supports_offline: Optional[bool] = None
    language: Optional[str] = None
    estimated_weeks: Optional[int] = None
    is_sequential: Optional[bool] = None
    price: Optional[str] = None
    currency: Optional[str] = None


def _check_course_permission(actor: User, course: Course) -> None:
    """
    Проверяет права на управление курсом.

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
            "Only admin, staff, or course author can manage this course",
            code="insufficient_permissions",
        )


class UpdateCourseCommand:
    """
    Command для обновления метаданных курса.

    Permissions: Admin, Staff, or Course Author
    """

    @staticmethod
    @transaction.atomic
    def execute(course_id: str, data: UpdateCourseData, actor: User) -> Course:
        """
        Обновляет метаданные курса.

        Immutable fields:
        - slug (после публикации)
        - created_by

        Args:
            course_id: UUID курса
            data: UpdateCourseData с новыми значениями (только changed fields)
            actor: Пользователь обновляющий курс

        Returns:
            Course instance с обновлёнными данными

        Raises:
            NotFoundError: если курс не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
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

        
        update_fields = []

        if data.title is not None:
            clean_title = data.title.strip()
            if len(clean_title) < 3:
                raise BusinessValidationError(
                    code="title_too_short",
                    lang="uz",
                    message="Course title must be at least 3 characters",
                )
            course.title = clean_title
            update_fields.append("title")

        if data.description is not None:
            course.description = data.description
            update_fields.append("description")

        if data.short_description is not None:
            course.short_description = data.short_description
            update_fields.append("short_description")

        if data.thumbnail_url is not None:
            course.thumbnail_url = data.thumbnail_url
            update_fields.append("thumbnail_url")

        if data.category_id is not None:
            if data.category_id:
                from src.backend.learning.domain.models import CourseCategory

                if not CourseCategory.objects.filter(
                    id=data.category_id, is_active=True
                ).exists():
                    raise NotFoundError(
                        f"Category {data.category_id} not found or inactive",
                        code="category_not_found",
                    )
            course.category_id = data.category_id
            update_fields.append("category_id")

        
        if data.supports_online is not None:
            course.supports_online = data.supports_online
            update_fields.append("supports_online")

        if data.supports_offline is not None:
            
            if not data.supports_offline and course.supports_offline:
                from src.backend.enrollment.domain.models import CourseEnrollment

                offline_count = CourseEnrollment.objects.filter(
                    course_id=course.id,
                    delivery_format="offline",
                    status="active",
                    deleted_at__isnull=True,  
                ).count()

                if offline_count > 0:
                    raise BusinessValidationError(
                        code="offline_enrollments_exist",
                        lang="uz",
                        message=(
                            f"Cannot disable offline mode: {offline_count} active offline enrollments exist. "
                            "Complete or drop them first."
                        ),
                    )

            course.supports_offline = data.supports_offline
            update_fields.append("supports_offline")

        
        if not course.supports_online and not course.supports_offline:
            raise BusinessValidationError(
                code="delivery_format_required",
                lang="uz",
                message="Course must support at least one delivery format (online or offline)",
            )

        if data.language is not None:
            course.language = data.language
            update_fields.append("language")

        if data.estimated_weeks is not None:
            if data.estimated_weeks <= 0:
                raise BusinessValidationError(
                    code="invalid_estimated_weeks",
                    lang="uz",
                    message="Estimated weeks must be greater than 0",
                )
            course.estimated_weeks = data.estimated_weeks
            update_fields.append("estimated_weeks")

        if data.is_sequential is not None:
            course.is_sequential = data.is_sequential
            update_fields.append("is_sequential")

        if data.price is not None:
            try:
                price_value = Decimal(str(data.price))
                if price_value < 0:
                    raise BusinessValidationError(
                        code="invalid_price",
                        lang="uz",
                        message="Price cannot be negative",
                    )
                course.price = price_value
                update_fields.append("price")
            except (InvalidOperation, ValueError):
                raise BusinessValidationError(
                    code="invalid_price",
                    lang="uz",
                    message="Invalid price format",
                )

        if data.currency is not None:
            if data.currency not in ['UZS', 'USD']:
                raise BusinessValidationError(
                    code="invalid_currency",
                    lang="uz",
                    message="Currency must be UZS or USD",
                )
            course.currency = data.currency
            update_fields.append("currency")

        
        if update_fields:
            update_fields.append("updated_at")
            course.save(update_fields=update_fields)

        
        

        return course

    @staticmethod
    @transaction.atomic
    def archive_course(course_id: str, actor: User) -> Course:
        """
        Архивирует курс (любой статус → archived).

        Args:
            course_id: UUID курса
            actor: Пользователь (admin/staff/author)

        Returns:
            Course instance (status='archived')

        Raises:
            NotFoundError: если курс не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если курс уже в архиве
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

        if course.status == "archived":
            raise BusinessValidationError(
                code="already_archived",
                lang="uz",
                message="Course is already archived",
            )

        
        course.status = "archived"
        course.save(update_fields=["status", "updated_at"])

        
        

        return course

    @staticmethod
    @transaction.atomic
    def delete_course(course_id: str, actor: User) -> Course:
        """
        Soft-delete курса (sets deleted_at).

        Business Rule: Нельзя удалить курс с любыми enrollments.
        Используй archive_course вместо delete.

        Args:
            course_id: UUID курса
            actor: Пользователь (admin/staff/author)

        Returns:
            Course instance (deleted_at set)

        Raises:
            NotFoundError: если курс не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если курс имеет enrollments
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

        
        from src.backend.enrollment.domain.models import CourseEnrollment

        enrollment_count = CourseEnrollment.objects.filter(
            course_id=course.id,
            deleted_at__isnull=True,  
        ).count()

        if enrollment_count > 0:
            raise BusinessValidationError(
                code="enrollments_exist",
                lang="uz",
                message=(
                    f"Cannot delete course: {enrollment_count} enrollments exist. "
                    "Use archive_course instead to preserve enrollment history."
                ),
            )

        
        course.deleted_at = timezone.now()
        course.save(update_fields=["deleted_at"])

        
        

        return course