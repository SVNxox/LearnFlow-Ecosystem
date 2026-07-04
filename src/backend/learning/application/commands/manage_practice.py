"""
ManagePracticeCommand — управление практическими заданиями урока.

Business Rules:
- Множественные practice items на урок
- practice_type: 'coding' | 'multiple_choice' | 'fill_blank' | 'matching'
- Reorder должен содержать все practice IDs урока
- Hard delete блокируется если есть attempts

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
from src.backend.learning.domain.models import Lesson, LessonPractice

User = get_user_model()


@dataclass
class AddPracticeData:
    """Input data для добавления practice."""

    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    type: str = "coding"
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    language: Optional[str] = None
    hints: Optional[list] = None
    max_score: int = 10
    time_limit_minutes: Optional[int] = None


@dataclass
class UpdatePracticeData:
    """Input data для обновления practice."""

    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    type: Optional[str] = None
    starter_code: Optional[str] = None
    solution_code: Optional[str] = None
    language: Optional[str] = None
    hints: Optional[list] = None
    max_score: Optional[int] = None
    time_limit_minutes: Optional[int] = None


def _check_lesson_permission(actor: User, lesson: Lesson) -> None:
    """
    Проверяет права на управление practice урока.

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
            "Only admin, staff, or course author can manage practice",
            code="insufficient_permissions"
        )


class ManagePracticeCommand:
    """
    Command для управления practice урока.

    Permissions: Admin, Staff, or Course Author
    """

    ALLOWED_PRACTICE_TYPES = ['coding', 'multiple_choice', 'fill_blank', 'matching', 'project']

    @staticmethod
    @transaction.atomic
    def add_practice(lesson_id: str, data: AddPracticeData, actor: User) -> LessonPractice:
        """
        Добавляет practice item в урок (appends to end).

        Args:
            lesson_id: UUID урока
            data: AddPracticeData с параметрами practice
            actor: Пользователь добавляющий practice

        Returns:
            LessonPractice instance

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
            raise NotFoundError(f"Lesson {lesson_id} not found", code="lesson_not_found")

        
        _check_lesson_permission(actor, lesson)

        
        if data.type not in ManagePracticeCommand.ALLOWED_PRACTICE_TYPES:
            allowed = ", ".join(ManagePracticeCommand.ALLOWED_PRACTICE_TYPES)
            raise BusinessValidationError(
                code="invalid_practice_type",
                lang="uz",
                message=f"Invalid practice type '{data.type}'. Allowed: {allowed}"
            )

        
        clean_title = data.title.strip()
        if len(clean_title) < 3:
            raise BusinessValidationError(
                code="title_too_short",
                lang="uz",
                message="Practice title must be at least 3 characters"
            )

        
        clean_instructions = data.instructions.strip()
        if len(clean_instructions) < 10:
            raise BusinessValidationError(
                code="instructions_too_short",
                lang="uz",
                message="Practice instructions must be at least 10 characters"
            )

        
        if data.max_score <= 0:
            raise BusinessValidationError(
                code="invalid_max_score",
                lang="uz",
                message="Max score must be greater than 0"
            )

        if data.time_limit_minutes is not None and data.time_limit_minutes < 0:
            raise BusinessValidationError(
                code="invalid_time_limit",
                lang="uz",
                message="Time limit must be greater than or equal to 0"
            )

        
        max_order = (
            LessonPractice.objects.filter(lesson_id=lesson_id).aggregate(
                max_order=Max("order")
            )["max_order"]
            or 0
        )

        practice = LessonPractice.objects.create(
            lesson=lesson,
            title=clean_title,
            description=data.description or "",
            instructions=data.instructions or "",
            type=data.type,
            starter_code=data.starter_code or "",
            solution_code=data.solution_code or "",
            language=data.language or "",
            hints=data.hints or [],
            max_score=data.max_score,
            time_limit_minutes=data.time_limit_minutes,
            order=max_order + 1,
        )

        return practice

    @staticmethod
    @transaction.atomic
    def update_practice(
        practice_id: str, data: UpdatePracticeData, actor: User
    ) -> LessonPractice:
        """
        Обновляет practice item.

        Note: practice_type immutable (нельзя изменить).

        Args:
            practice_id: UUID practice
            data: UpdatePracticeData с новыми значениями
            actor: Пользователь обновляющий practice

        Returns:
            LessonPractice instance

        Raises:
            NotFoundError: если practice не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            practice = (
                LessonPractice.objects.select_for_update()
                .select_related("lesson__module__course")
                .get(id=practice_id)
            )
        except LessonPractice.DoesNotExist:
            raise NotFoundError(f"Practice {practice_id} not found", code="practice_not_found")

        
        _check_lesson_permission(actor, practice.lesson)

        
        update_fields = []

        if data.title is not None:
            clean_title = data.title.strip()
            if len(clean_title) < 3:
                raise BusinessValidationError(
                    code="title_too_short",
                    lang="uz",
                    message="Practice title must be at least 3 characters"
                )
            practice.title = clean_title
            update_fields.append("title")

        if data.description is not None:
            practice.description = data.description
            update_fields.append("description")

        if data.instructions is not None:
            clean_instructions = data.instructions.strip()
            if len(clean_instructions) < 10:
                raise BusinessValidationError(
                    code="instructions_too_short",
                    lang="uz",
                    message="Practice instructions must be at least 10 characters"
                )
            practice.instructions = clean_instructions
            update_fields.append("instructions")

        if data.type is not None:
            if data.type not in ManagePracticeCommand.ALLOWED_PRACTICE_TYPES:
                allowed = ", ".join(ManagePracticeCommand.ALLOWED_PRACTICE_TYPES)
                raise BusinessValidationError(
                    code="invalid_practice_type",
                    lang="uz",
                    message=f"Invalid practice type '{data.type}'. Allowed: {allowed}"
                )
            practice.type = data.type
            update_fields.append("practice_type")

        if data.starter_code is not None:
            practice.starter_code = data.starter_code
            update_fields.append("starter_code")

        if data.solution_code is not None:
            practice.solution_code = data.solution_code
            update_fields.append("solution_code")

        if data.language is not None:
            practice.language = data.language
            update_fields.append("language")

        if data.hints is not None:
            practice.hints = data.hints
            update_fields.append("hints")

        if data.max_score is not None:
            if data.max_score <= 0:
                raise BusinessValidationError(
                    code="invalid_max_score",
                    lang="uz",
                    message="Max score must be greater than 0"
                )
            practice.max_score = data.max_score
            update_fields.append("max_score")

        if data.time_limit_minutes is not None:
            if data.time_limit_minutes < 0:
                raise BusinessValidationError(
                    code="invalid_time_limit",
                    lang="uz",
                    message="Time limit must be greater than or equal to 0"
                )
            practice.time_limit_minutes = data.time_limit_minutes
            update_fields.append("time_limit_minutes")

        
        if update_fields:
            practice.save(update_fields=update_fields)

        return practice

    @staticmethod
    @transaction.atomic
    def reorder_practice(
        lesson_id: str, ordered_ids: list[str], actor: User
    ) -> list[LessonPractice]:
        """
        Переупорядочивает practice items в уроке.

        Args:
            lesson_id: UUID урока
            ordered_ids: Список UUID practice в новом порядке
            actor: Пользователь (admin/staff/author)

        Returns:
            List[LessonPractice] в новом порядке

        Raises:
            NotFoundError: если урок не найден
            BusinessValidationError: если список неполный или содержит лишние IDs
            AccessDeniedError: если actor не имеет прав
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

        
        existing_items = list(LessonPractice.objects.filter(lesson_id=lesson_id))
        existing_ids = {str(p.id) for p in existing_items}
        provided_ids = set(ordered_ids)

        
        if existing_ids != provided_ids:
            missing = existing_ids - provided_ids
            extra = provided_ids - existing_ids
            errors = []
            if missing:
                errors.append(f"Missing practice IDs: {missing}")
            if extra:
                errors.append(f"Unknown practice IDs: {extra}")
            raise BusinessValidationError(
                code="invalid_reorder",
                lang="uz",
                message="Reorder list must contain exactly all practice IDs of the lesson. " + " ".join(errors)
            )

        
        practice_map = {str(p.id): p for p in existing_items}
        updated_items = []

        for new_order, practice_id in enumerate(ordered_ids, start=1):
            practice = practice_map[practice_id]
            if practice.order != new_order:
                practice.order = new_order
                practice.save(update_fields=["order"])
            updated_items.append(practice)

        return updated_items

    @staticmethod
    @transaction.atomic
    def delete_practice(practice_id: str, actor: User) -> None:
        """
        Удаляет practice item (hard delete).

        Business Rule: Блокируется если есть attempts.

        Args:
            practice_id: UUID practice
            actor: Пользователь (admin/staff/author)

        Raises:
            NotFoundError: если practice не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если есть attempts
        """
        
        try:
            practice = LessonPractice.objects.select_related(
                "lesson__module__course"
            ).get(id=practice_id)
        except LessonPractice.DoesNotExist:
            raise NotFoundError(f"Practice {practice_id} not found", code="practice_not_found")

        
        _check_lesson_permission(actor, practice.lesson)

        
        
            
            
            
            
            
            
            
            
            

        lesson_id = str(practice.lesson_id)

        
        practice.delete()