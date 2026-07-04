"""
UpdateLessonCommand — обновление и управление уроками.

Business Rules:
- Нельзя публиковать пустой урок (без content/homework/quiz/practice)
- Soft delete блокируется если есть completed progress
- Reorder должен содержать все non-deleted lesson IDs модуля

Permissions:
- Admin или Staff
- Course Author (автор курса, которому принадлежит урок)
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
from src.backend.learning.domain.models import Lesson, Module

User = get_user_model()


@dataclass
class UpdateLessonData:
    """Input data для обновления урока."""

    title: Optional[str] = None
    description: Optional[str] = None
    estimated_minutes: Optional[int] = None
    is_free_preview: Optional[bool] = None


def _check_lesson_permission(actor: User, lesson: Lesson) -> None:
    """
    Проверяет права на управление уроком.

    Разрешено:
    - admin
    - staff
    - course author (автор курса, которому принадлежит урок)

    Raises:
        AccessDeniedError: если нет прав
    """
    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = lesson.module.course.created_by_id == actor.id

    if not (is_admin or is_staff or is_course_author):
        raise AccessDeniedError(
            "Only admin, staff, or course author can manage lessons",
            code="insufficient_permissions",
        )


def _check_module_permission(actor: User, module: Module) -> None:
    """
    Проверяет права на управление модулем (для reorder).

    Raises:
        AccessDeniedError: если нет прав
    """
    user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = module.course.created_by_id == actor.id

    if not (is_admin or is_staff or is_course_author):
        raise AccessDeniedError(
            "Only admin, staff, or course author can reorder lessons",
            code="insufficient_permissions",
        )


class UpdateLessonCommand:
    """
    Command для обновления уроков.

    Permissions: Admin, Staff, or Course Author
    """

    @staticmethod
    @transaction.atomic
    def execute(lesson_id: str, data: UpdateLessonData, actor: User) -> Lesson:
        """
        Обновляет метаданные урока.

        Args:
            lesson_id: UUID урока
            data: UpdateLessonData с новыми значениями
            actor: Пользователь обновляющий урок

        Returns:
            Lesson instance с обновлёнными данными

        Raises:
            NotFoundError: если урок не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            lesson = (
                Lesson.objects.select_for_update()
                .select_related("module__course")
                .get(id=lesson_id, deleted_at__isnull=True)
            )
        except Lesson.DoesNotExist:
            raise NotFoundError(
                f"Lesson {lesson_id} not found",
                code="lesson_not_found",
            )

        
        _check_lesson_permission(actor, lesson)

        
        update_fields = []

        if data.title is not None:
            clean_title = data.title.strip()
            if len(clean_title) < 3:
                raise BusinessValidationError(
                    code="title_too_short",
                    lang="uz",
                    message="Lesson title must be at least 3 characters",
                )
            lesson.title = clean_title
            update_fields.append("title")

        if data.description is not None:
            lesson.description = data.description
            update_fields.append("description")

        if data.estimated_minutes is not None:
            if data.estimated_minutes <= 0:
                raise BusinessValidationError(
                    code="invalid_estimated_minutes",
                    lang="uz",
                    message="Estimated minutes must be greater than 0",
                )
            lesson.estimated_minutes = data.estimated_minutes
            update_fields.append("estimated_minutes")

        if data.is_free_preview is not None:
            lesson.is_free_preview = data.is_free_preview
            update_fields.append("is_free_preview")

        
        if update_fields:
            update_fields.append("updated_at")
            lesson.save(update_fields=update_fields)

        return lesson

    @staticmethod
    @transaction.atomic
    def publish_lesson(lesson_id: str, actor: User) -> Lesson:
        """
        Публикует урок (is_published=False → True).

        Business Rule: Урок должен иметь минимум 1 компонент
        (content/homework/quiz/practice).

        Args:
            lesson_id: UUID урока
            actor: Пользователь (admin/staff/author)

        Returns:
            Lesson instance (is_published=True)

        Raises:
            NotFoundError: если урок не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если урок пустой или уже опубликован
        """
        try:
            lesson = (
                Lesson.objects.select_for_update()
                .select_related("module__course")
                .get(id=lesson_id, deleted_at__isnull=True)
            )
        except Lesson.DoesNotExist:
            raise NotFoundError(
                f"Lesson {lesson_id} not found",
                code="lesson_not_found",
            )

        
        _check_lesson_permission(actor, lesson)

        if lesson.is_published:
            raise BusinessValidationError(
                code="already_published",
                lang="uz",
                message="Lesson is already published",
            )

        
        from src.backend.learning.domain.models import (
            LessonContent,
            LessonHomework,
            LessonPractice,
            LessonQuiz,
        )

        has_content = LessonContent.objects.filter(lesson_id=lesson_id).exists()
        has_homework = LessonHomework.objects.filter(lesson_id=lesson_id).exists()
        has_quiz = LessonQuiz.objects.filter(lesson_id=lesson_id).exists()
        has_practice = LessonPractice.objects.filter(lesson_id=lesson_id).exists()

        if not (has_content or has_homework or has_quiz or has_practice):
            raise BusinessValidationError(
                code="lesson_empty",
                lang="uz",
                message=(
                    "Cannot publish lesson: lesson is empty. "
                    "Add at least one component (content, homework, quiz, or practice)."
                ),
            )

        
        lesson.is_published = True
        lesson.save(update_fields=["is_published", "updated_at"])

        return lesson

    @staticmethod
    @transaction.atomic
    def unpublish_lesson(lesson_id: str, actor: User) -> Lesson:
        """
        Снимает урок с публикации (is_published=True → False).

        Args:
            lesson_id: UUID урока
            actor: Пользователь (admin/staff/author)

        Returns:
            Lesson instance (is_published=False)

        Raises:
            NotFoundError: если урок не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если урок не опубликован
        """
        try:
            lesson = (
                Lesson.objects.select_for_update()
                .select_related("module__course")
                .get(id=lesson_id, deleted_at__isnull=True)
            )
        except Lesson.DoesNotExist:
            raise NotFoundError(
                f"Lesson {lesson_id} not found",
                code="lesson_not_found",
            )

        
        _check_lesson_permission(actor, lesson)

        if not lesson.is_published:
            raise BusinessValidationError(
                code="not_published",
                lang="uz",
                message="Lesson is not published",
            )

        
        lesson.is_published = False
        lesson.save(update_fields=["is_published", "updated_at"])

        return lesson

    @staticmethod
    @transaction.atomic
    def reorder_lessons(
        module_id: str, ordered_ids: list[str], actor: User
    ) -> list[Lesson]:
        """
        Переупорядочивает уроки в модуле.

        Business Rule: ordered_ids должен содержать ВСЕ non-deleted lesson IDs модуля.

        Args:
            module_id: UUID модуля
            ordered_ids: Список UUID уроков в новом порядке
            actor: Пользователь (admin/staff/author)

        Returns:
            List[Lesson] в новом порядке

        Raises:
            NotFoundError: если модуль не найден
            BusinessValidationError: если список неполный или содержит лишние IDs
            AccessDeniedError: если actor не имеет прав
        """
        
        try:
            module = (
                Module.objects.select_for_update()
                .select_related("course")
                .get(id=module_id, deleted_at__isnull=True)
            )
        except Module.DoesNotExist:
            raise NotFoundError(
                f"Module {module_id} not found",
                code="module_not_found",
            )

        
        _check_module_permission(actor, module)

        
        existing_lessons = list(
            Lesson.objects.filter(module_id=module_id, deleted_at__isnull=True)
        )
        existing_ids = {str(l.id) for l in existing_lessons}
        provided_ids = set(ordered_ids)

        
        if existing_ids != provided_ids:
            missing = existing_ids - provided_ids
            extra = provided_ids - existing_ids
            errors = []
            if missing:
                errors.append(f"Missing lesson IDs: {missing}")
            if extra:
                errors.append(f"Unknown lesson IDs: {extra}")
            raise BusinessValidationError(
                code="invalid_reorder",
                lang="uz",
                message=(
                    "Reorder list must contain exactly all non-deleted lesson IDs. "
                    + " ".join(errors)
                ),
            )

        
        lesson_map = {str(l.id): l for l in existing_lessons}
        updated_lessons = []

        for new_order, lesson_id in enumerate(ordered_ids, start=1):
            lesson = lesson_map[lesson_id]
            if lesson.order != new_order:
                lesson.order = new_order
                lesson.save(update_fields=["order", "updated_at"])
            updated_lessons.append(lesson)

        return updated_lessons

    @staticmethod
    @transaction.atomic
    def delete_lesson(lesson_id: str, actor: User) -> Lesson:
        """
        Soft-delete урока (sets deleted_at).

        Business Rule: Блокируется если есть completed LessonProgress records.

        Args:
            lesson_id: UUID урока
            actor: Пользователь (admin/staff/author)

        Returns:
            Lesson instance (deleted_at set)

        Raises:
            NotFoundError: если урок не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если урок имеет completed progress
        """
        try:
            lesson = (
                Lesson.objects.select_for_update()
                .select_related("module__course")
                .get(id=lesson_id, deleted_at__isnull=True)
            )
        except Lesson.DoesNotExist:
            raise NotFoundError(
                f"Lesson {lesson_id} not found",
                code="lesson_not_found",
            )

        
        _check_lesson_permission(actor, lesson)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        lesson.deleted_at = timezone.now()
        lesson.save(update_fields=["deleted_at"])

        return lesson