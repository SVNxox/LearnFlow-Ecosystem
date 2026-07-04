"""
CreateModuleCommand — создание модуля внутри курса.

Business Rules:
- Модуль создаётся в конце списка (max order + 1)
- Модуль создаётся unpublished по умолчанию
- Курс должен существовать и не быть удалённым

Permissions:
- Admin или Staff
- Course Author (автор курса)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max

from src.backend.core.exceptions import AccessDeniedError, BusinessValidationError, NotFoundError
from src.backend.learning.domain.models import Course, Module

User = get_user_model()


@dataclass
class CreateModuleData:
    """Input data для создания модуля."""

    title: str
    description: Optional[str] = None
    estimated_hours: Optional[int] = None


class CreateModuleCommand:
    """
    Command для создания модуля внутри курса.

    Permissions: Admin, Staff, or Course Author
    """

    @staticmethod
    @transaction.atomic
    def execute(course_id: str, data: CreateModuleData, actor: User) -> Module:
        """
        Создаёт новый модуль в курсе.

        Args:
            course_id: UUID курса
            data: CreateModuleData с параметрами модуля
            actor: Пользователь создающий модуль

        Returns:
            Module instance (is_published=False)

        Raises:
            NotFoundError: если курс не найден или удалён
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            course = Course.objects.select_for_update().get(
                id=course_id, deleted_at__isnull=True
            )
        except Course.DoesNotExist:
            raise NotFoundError(f"Course {course_id} not found", code="course_not_found")

        
        user_roles = actor.get_roles() if hasattr(actor, 'get_roles') else []

        is_admin = 'admin' in user_roles
        is_staff = 'staff' in user_roles
        is_course_author = course.created_by_id == actor.id

        if not (is_admin or is_staff or is_course_author):
            raise AccessDeniedError(
                "Only admin, staff, or course author can create modules",
                code="insufficient_permissions"
            )

        
        clean_title = data.title.strip()
        if len(clean_title) < 3:
            raise BusinessValidationError(
                code="title_too_short",
                lang="uz",
                message="Module title must be at least 3 characters long"
            )

        
        if data.estimated_hours is not None and data.estimated_hours <= 0:
            raise BusinessValidationError(
                code="invalid_estimated_hours",
                lang="uz",
                message="Estimated hours must be greater than 0"
            )

        
        max_order = (
            Module.objects.filter(course_id=course_id, deleted_at__isnull=True).aggregate(
                max_order=Max("order")
            )["max_order"]
            or 0
        )

        
        module = Module.objects.create(
            course=course,
            title=clean_title,
            description=data.description,
            estimated_hours=data.estimated_hours,
            order=max_order + 1,
            is_published=False,  
        )

        return module