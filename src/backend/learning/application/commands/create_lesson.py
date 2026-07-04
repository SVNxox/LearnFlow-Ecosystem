"""
CreateLessonCommand — создание урока внутри модуля.

Business Rules:
- Урок создаётся в конце списка (max order + 1)
- Урок создаётся unpublished по умолчанию
- Модуль должен существовать и не быть удалённым

Permissions:
- Admin или Staff
- Course Author (автор курса, которому принадлежит модуль)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max

from src.backend.core.exceptions import NotFoundError, BusinessValidationError, AccessDeniedError
from src.backend.learning.domain.models import Lesson, Module

User = get_user_model()


@dataclass
class CreateLessonData:
    """Input data для создания урока."""

    title: str
    description: Optional[str] = None
    estimated_minutes: Optional[int] = None
    is_free_preview: bool = False


class CreateLessonCommand:
    """
    Command для создания урока внутри модуля.

    Permissions: Admin, Staff, or Course Author
    """

    @staticmethod
    @transaction.atomic
    def execute(module_id: str, data: CreateLessonData, actor: User) -> Lesson:
        """
        Создаёт новый урок в модуле.

        Args:
            module_id: UUID модуля
            data: CreateLessonData с параметрами урока
            actor: Пользователь создающий урок

        Returns:
            Lesson instance (is_published=False)

        Raises:
            NotFoundError: если модуль не найден или удалён
            AccessDeniedError: если actor не имеет прав
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

        
        user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

        is_admin = 'admin' in user_roles
        is_staff = 'staff' in user_roles
        is_course_author = module.course.created_by_id == actor.id

        if not (is_admin or is_staff or is_course_author):
            raise AccessDeniedError(
                "Only admin, staff, or course author can create lessons",
                code="insufficient_permissions"
            )

        
        clean_title = data.title.strip()
        if len(clean_title) < 3:
            raise BusinessValidationError(
                code="title_too_short",
                lang="uz",
                message="Lesson title must be at least 3 characters long"
            )

        
        if data.estimated_minutes is not None and data.estimated_minutes <= 0:
            raise BusinessValidationError(
                code="invalid_estimated_minutes",
                lang="uz",
                message="Estimated minutes must be greater than 0"
            )

        
        max_order = (
            Lesson.objects.filter(module_id=module_id, deleted_at__isnull=True).aggregate(
                max_order=Max("order")
            )["max_order"]
            or 0
        )

        
        lesson = Lesson.objects.create(
            module=module,
            title=clean_title,
            description=data.description,
            estimated_minutes=data.estimated_minutes,
            is_free_preview=data.is_free_preview,
            order=max_order + 1,
            is_published=False,  
        )

        return lesson