"""
ManageContentCommand — управление контентом урока.

Business Rules:
- Content type immutable после создания
- Минимум одно из url/body должно быть заполнено
- Reorder должен содержать все content IDs урока
- Hard delete (не soft) — UserProgress records сохраняются

Permissions:
- Admin или Staff
- Course Author (автор курса, которому принадлежит урок)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max

from src.backend.core.exceptions import AccessDeniedError, BusinessValidationError, NotFoundError
from src.backend.learning.domain.models import Lesson, LessonContent

User = get_user_model()


@dataclass
class AddContentData:
    """Input data для добавления контента."""
    content_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    body: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None  
    metadata: Optional[dict] = None  
    is_required: bool = False
    is_downloadable: bool = False


@dataclass
class UpdateContentData:
    """Input data для обновления контента."""
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    body: Optional[str] = None
    duration_seconds: Optional[int] = None
    file_size_bytes: Optional[int] = None  
    metadata: Optional[dict] = None  
    is_required: Optional[bool] = None
    is_downloadable: Optional[bool] = None


def _check_lesson_permission(actor: User, lesson: Lesson) -> None:
    """
    Проверяет права на управление контентом урока.

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
            "Only admin, staff, or course author can manage lesson content",
            code="insufficient_permissions"
        )


class ManageContentCommand:
    """
    Command для управления контентом урока.

    Permissions: Admin, Staff, or Course Author
    """

    ALLOWED_CONTENT_TYPES = ['video', 'pdf', 'slides', 'text', 'link', 'recording', 'code']

    @staticmethod
    @transaction.atomic
    def add_content(lesson_id: str, data: AddContentData, actor: User) -> LessonContent:
        """Добавляет контент элемент в урок."""
        try:
            lesson = (
                Lesson.objects.select_for_update()
                .select_related("module__course")
                .get(id=lesson_id, deleted_at__isnull=True)
            )
        except Lesson.DoesNotExist:
            raise NotFoundError(f"Lesson {lesson_id} not found", code="lesson_not_found")

        _check_lesson_permission(actor, lesson)

        
        if data.content_type not in ManageContentCommand.ALLOWED_CONTENT_TYPES:
            allowed = ", ".join(ManageContentCommand.ALLOWED_CONTENT_TYPES)
            raise BusinessValidationError(
                code="invalid_content_type",
                lang="uz",
                message=f"Invalid content type. Allowed: {allowed}"
            )

        
        if not data.url and not data.body:
            raise BusinessValidationError(
                code="content_required",
                lang="uz",
                message="Either url or body must be provided"
            )

        
        if data.duration_seconds is not None and data.duration_seconds < 0:
            raise BusinessValidationError(
                code="invalid_duration",
                lang="uz",
                message="Duration seconds must be greater than or equal to 0"
            )

        
        max_order = (
                LessonContent.objects.filter(lesson_id=lesson_id).aggregate(
                    max_order=Max("order")
                )["max_order"]
                or 0
        )

        
        content = LessonContent.objects.create(
            lesson=lesson,
            type=data.content_type,
            title=data.title,
            description=data.description or '',
            url=data.url or '',
            body=data.body or '',
            duration_seconds=data.duration_seconds,
            file_size_bytes=data.file_size_bytes,
            metadata=data.metadata or {},
            is_required=data.is_required,
            is_downloadable=data.is_downloadable,
            order=max_order + 1,
        )

        return content

    @staticmethod
    @transaction.atomic
    def update_content(content_id: str, data: UpdateContentData, actor: User) -> LessonContent:
        """Обновляет контент элемент."""
        try:
            content = (
                LessonContent.objects.select_for_update()
                .select_related("lesson__module__course")
                .get(id=content_id)
            )
        except LessonContent.DoesNotExist:
            raise NotFoundError(f"Content {content_id} not found", code="content_not_found")

        _check_lesson_permission(actor, content.lesson)

        update_fields = []

        if data.title is not None:
            content.title = data.title
            update_fields.append("title")

        if data.description is not None:
            content.description = data.description
            update_fields.append("description")

        if data.url is not None:
            content.url = data.url
            update_fields.append("url")

        if data.body is not None:
            content.body = data.body
            update_fields.append("body")

        if data.duration_seconds is not None:
            if data.duration_seconds < 0:
                raise BusinessValidationError(
                    code="invalid_duration",
                    lang="uz",
                    message="Duration seconds must be greater than or equal to 0"
                )
            content.duration_seconds = data.duration_seconds
            update_fields.append("duration_seconds")

        if data.file_size_bytes is not None:
            content.file_size_bytes = data.file_size_bytes
            update_fields.append("file_size_bytes")

        if data.metadata is not None:
            content.metadata = data.metadata
            update_fields.append("metadata")

        if data.is_required is not None:
            content.is_required = data.is_required
            update_fields.append("is_required")

        if data.is_downloadable is not None:
            content.is_downloadable = data.is_downloadable
            update_fields.append("is_downloadable")

        
        if not content.url and not content.body:
            raise BusinessValidationError(
                code="content_required",
                lang="uz",
                message="Either url or body must be provided"
            )

        if update_fields:
            update_fields.append("updated_at")
            content.save(update_fields=update_fields)

        return content

    @staticmethod
    @transaction.atomic
    def reorder_content(lesson_id: str, ordered_ids: list[str], actor: User) -> list[LessonContent]:
        """
        Переупорядочивает контент элементы в уроке.

        Использует bulk_update для атомарного обновления, избегая конфликтов уникальности.
        """
        
        try:
            lesson = (
                Lesson.objects.select_for_update()
                .select_related("module__course")
                .get(id=lesson_id, deleted_at__isnull=True)
            )
        except Lesson.DoesNotExist:
            raise NotFoundError(f"Lesson {lesson_id} not found", code="lesson_not_found")

        
        _check_lesson_permission(actor, lesson)

        
        existing_items = list(LessonContent.objects.filter(lesson_id=lesson_id))
        existing_ids = {str(c.id) for c in existing_items}
        provided_ids = set(ordered_ids)

        
        if existing_ids != provided_ids:
            missing = existing_ids - provided_ids
            extra = provided_ids - existing_ids
            errors = []
            if missing:
                errors.append(f"Missing content IDs: {missing}")
            if extra:
                errors.append(f"Unknown content IDs: {extra}")
            raise BusinessValidationError(
                code="invalid_reorder",
                lang="uz",
                message="Reorder list must contain exactly all content IDs of the lesson. " + " ".join(errors)
            )

        
        content_map = {str(c.id): c for c in existing_items}
        items_to_update = []

        for new_order, content_id in enumerate(ordered_ids, start=1):
            content = content_map[content_id]
            if content.order != new_order:
                content.order = new_order
                items_to_update.append(content)

        
        if items_to_update:
            LessonContent.objects.bulk_update(items_to_update, ['order'])

        return LessonContent.objects.filter(lesson_id=lesson_id).order_by('order')

    @staticmethod
    @transaction.atomic
    def delete_content(content_id: str, actor: User) -> None:
        """
        Удаляет контент элемент (hard delete).

        Note: UserProgress ContentView records сохраняются (orphaned).

        Args:
            content_id: UUID контента
            actor: Пользователь (admin/staff/author)

        Raises:
            NotFoundError: если контент не найден
            AccessDeniedError: если actor не имеет прав
        """
        
        try:
            content = LessonContent.objects.select_related(
                "lesson__module__course"
            ).get(id=content_id)
        except LessonContent.DoesNotExist:
            raise NotFoundError(f"Content {content_id} not found", code="content_not_found")

        
        _check_lesson_permission(actor, content.lesson)

        
        content.delete()