"""
UpdateModuleCommand — обновление и управление модулями.

Business Rules:
- Нельзя публиковать модуль без опубликованных уроков
- Reorder должен содержать все non-deleted module IDs
- Soft delete не удаляет lessons

Permissions:
- Admin/Staff: полный доступ ко всем модулям
- Course Author: полный доступ к своим курсам
- Mentor/Student: только просмотр published модулей (через ModuleCatalogQuery)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from src.backend.core.exceptions import AccessDeniedError, BusinessValidationError, NotFoundError
from src.backend.learning.domain.models import Module, Course

User = get_user_model()


def _check_module_permission(actor: User, module: Module) -> None:
    """
    Проверяет права на модуль.

    Разрешено:
    - admin или staff (любая роль)
    - course author (создатель курса)

    Запрещено:
    - mentor, student, anonymous
    """
    
    user_roles = []
    if hasattr(actor, 'get_roles'):
        try:
            user_roles = actor.get_roles()
        except Exception:
            user_roles = []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = module.course.created_by_id == actor.id

    if not (is_admin or is_staff or is_course_author):
        raise AccessDeniedError(
            "Only admin, staff, or course author can manage modules",
            code="insufficient_permissions"
        )


def _check_course_permission(actor: User, course: Course) -> None:
    """
    Проверяет права на курс.
    """
    user_roles = []
    if hasattr(actor, 'get_roles'):
        try:
            user_roles = actor.get_roles()
        except Exception:
            user_roles = []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = course.created_by_id == actor.id

    if not (is_admin or is_staff or is_course_author):
        raise AccessDeniedError(
            "Only admin, staff, or course author can manage this course",
            code="insufficient_permissions"
        )


@dataclass
class UpdateModuleData:
    """Input data для обновления модуля."""
    title: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[int] = None


class UpdateModuleCommand:
    """
    Command для обновления модулей.

    Permissions: Admin, Staff, or Course Author
    """

    @staticmethod
    @transaction.atomic
    def execute(module_id: str, data: UpdateModuleData, actor: User) -> Module:
        """
        Обновляет метаданные модуля.

        Raises:
            NotFoundError: если модуль не найден
            AccessDeniedError: если нет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            module = (
                Module.objects.select_for_update()
                .select_related("course")
                .get(id=module_id, deleted_at__isnull=True)
            )
        except Module.DoesNotExist:
            raise NotFoundError(f"Module {module_id} not found", code="module_not_found")

        
        _check_module_permission(actor, module)

        
        update_fields = []

        if data.title is not None:
            clean_title = data.title.strip()
            if len(clean_title) < 3:
                raise BusinessValidationError(
                    code="title_too_short",
                    lang="uz",
                    message="Title must be at least 3 characters long"
                )
            module.title = clean_title
            update_fields.append("title")

        if data.description is not None:
            module.description = data.description.strip()
            update_fields.append("description")

        if data.estimated_hours is not None:
            if data.estimated_hours <= 0:
                raise BusinessValidationError(
                    code="invalid_estimated_hours",
                    lang="uz",
                    message="Estimated hours must be greater than 0"
                )
            module.estimated_hours = data.estimated_hours
            update_fields.append("estimated_hours")

        
        if update_fields:
            update_fields.append("updated_at")
            module.save(update_fields=update_fields)

        return module

    @staticmethod
    @transaction.atomic
    def publish_module(module_id: str, actor: User) -> Module:
        """
        Публикует модуль (is_published=False → True).

        Business Rule: Модуль должен иметь минимум 1 опубликованный урок.
        """
        try:
            module = (
                Module.objects.select_for_update()
                .select_related("course")
                .get(id=module_id, deleted_at__isnull=True)
            )
        except Module.DoesNotExist:
            raise NotFoundError(f"Module {module_id} not found", code="module_not_found")

        
        _check_module_permission(actor, module)

        if module.is_published:
            raise BusinessValidationError(
                code="already_published",
                lang="uz",
                message="Module is already published"
            )

        
        published_lessons_count = module.lessons.filter(
            is_published=True, deleted_at__isnull=True
        ).count()

        if published_lessons_count == 0:
            raise BusinessValidationError(
                code="no_published_lessons",
                lang="uz",
                message="Cannot publish module: no published lessons found. Create and publish at least one lesson first."
            )

        
        module.is_published = True
        module.save(update_fields=["is_published", "updated_at"])

        return module

    @staticmethod
    @transaction.atomic
    def unpublish_module(module_id: str, actor: User) -> Module:
        """
        Снимает модуль с публикации (is_published=True → False).
        """
        try:
            module = (
                Module.objects.select_for_update()
                .select_related("course")
                .get(id=module_id, deleted_at__isnull=True)
            )
        except Module.DoesNotExist:
            raise NotFoundError(f"Module {module_id} not found", code="module_not_found")

        
        _check_module_permission(actor, module)

        if not module.is_published:
            raise BusinessValidationError(
                code="not_published",
                lang="uz",
                message="Module is not published"
            )

        
        module.is_published = False
        module.save(update_fields=["is_published", "updated_at"])

        return module

    @staticmethod
    @transaction.atomic
    def reorder_modules(course_id: str, ordered_ids: list[str], actor: User) -> list[Module]:
        """
        Переупорядочивает модули в курсе.

        Business Rule: ordered_ids должен содержать ВСЕ non-deleted module IDs курса.
        """
        
        try:
            course = Course.objects.select_for_update().get(
                id=course_id, deleted_at__isnull=True
            )
        except Course.DoesNotExist:
            raise NotFoundError(f"Course {course_id} not found", code="course_not_found")

        
        _check_course_permission(actor, course)

        
        existing_modules = list(
            Module.objects.filter(course_id=course_id, deleted_at__isnull=True)
        )
        existing_ids = {str(m.id) for m in existing_modules}
        provided_ids = set(ordered_ids)

        
        if existing_ids != provided_ids:
            missing = existing_ids - provided_ids
            extra = provided_ids - existing_ids
            errors = []
            if missing:
                errors.append(f"Missing module IDs: {missing}")
            if extra:
                errors.append(f"Unknown module IDs: {extra}")
            raise BusinessValidationError(
                code="invalid_reorder",
                lang="uz",
                message="Reorder list must contain exactly all non-deleted module IDs. " + " ".join(errors)
            )

        
        module_map = {str(m.id): m for m in existing_modules}
        updated_modules = []

        for new_order, module_id in enumerate(ordered_ids, start=1):
            module = module_map[module_id]
            if module.order != new_order:
                module.order = new_order
                module.save(update_fields=["order", "updated_at"])
            updated_modules.append(module)

        return updated_modules

    @staticmethod
    @transaction.atomic
    def delete_module(module_id: str, actor: User) -> Module:
        """
        Soft-delete модуля (sets deleted_at).

        Note: Lessons НЕ удаляются вместе с модулем.
        """
        try:
            module = (
                Module.objects.select_for_update()
                .select_related("course")
                .get(id=module_id, deleted_at__isnull=True)
            )
        except Module.DoesNotExist:
            raise NotFoundError(f"Module {module_id} not found", code="module_not_found")

        
        _check_module_permission(actor, module)

        
        module.deleted_at = timezone.now()
        module.save(update_fields=["deleted_at"])

        return module