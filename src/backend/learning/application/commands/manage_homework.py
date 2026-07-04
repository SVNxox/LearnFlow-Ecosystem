"""
ManageHomeworkCommand — управление домашними заданиями урока.

Business Rules:
- Только одно homework на урок (upsert pattern)
- Нельзя удалить homework если есть submissions
- homework_type: 'text' | 'file_upload' | 'coding' | 'project'

Permissions:
- Admin или Staff
- Course Author (автор курса, которому принадлежит урок)
"""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from src.backend.core.exceptions import AccessDeniedError, BusinessValidationError, NotFoundError
from src.backend.learning.domain.models import Lesson, LessonHomework

User = get_user_model()


@dataclass
class SetHomeworkData:
    """Input data для установки homework."""

    title: str
    instructions: str
    homework_type: str  
    max_score: int = 100
    required_files: Optional[list] = None  


def _check_lesson_permission(actor: User, lesson: Lesson) -> None:
    """
    Проверяет права на управление homework урока.

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
            "Only admin, staff, or course author can manage homework",
            code="insufficient_permissions"
        )


class ManageHomeworkCommand:
    """
    Command для управления homework урока.

    Permissions: Admin, Staff, or Course Author
    """

    ALLOWED_HOMEWORK_TYPES = ['text', 'file_upload', 'coding', 'project']

    @staticmethod
    @transaction.atomic
    def set_homework(lesson_id: str, data: SetHomeworkData, actor: User) -> LessonHomework:
        """
        Устанавливает или заменяет homework урока (upsert pattern).

        Args:
            lesson_id: UUID урока
            data: SetHomeworkData с параметрами homework
            actor: Пользователь устанавливающий homework

        Returns:
            LessonHomework instance

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

        
        if data.homework_type not in ManageHomeworkCommand.ALLOWED_HOMEWORK_TYPES:
            allowed = ", ".join(ManageHomeworkCommand.ALLOWED_HOMEWORK_TYPES)
            raise BusinessValidationError(
                code="invalid_homework_type",
                lang="uz",
                message=f"Invalid homework type '{data.homework_type}'. Allowed: {allowed}"
            )

        
        clean_title = data.title.strip()
        if len(clean_title) < 3:
            raise BusinessValidationError(
                code="title_too_short",
                lang="uz",
                message="Homework title must be at least 3 characters"
            )

        
        clean_instructions = data.instructions.strip()
        if len(clean_instructions) < 10:
            raise BusinessValidationError(
                code="instructions_too_short",
                lang="uz",
                message="Homework instructions must be at least 10 characters"
            )

        
        if data.max_score <= 0:
            raise BusinessValidationError(
                code="invalid_max_score",
                lang="uz",
                message="Max score must be greater than 0"
            )

        
        homework, created = LessonHomework.objects.update_or_create(
            lesson=lesson,
            defaults={
                "title": clean_title,
                "instructions": clean_instructions,
                "homework_type": data.homework_type,
                "max_score": data.max_score,
                "required_files": data.required_files or [],
            },
        )

        return homework

    @staticmethod
    @transaction.atomic
    def remove_homework(lesson_id: str, actor: User) -> None:
        """
        Удаляет homework урока (hard delete).

        Business Rule: Блокируется если есть существующие submissions.

        Args:
            lesson_id: UUID урока
            actor: Пользователь (admin/staff/author)

        Raises:
            NotFoundError: если урок или homework не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если есть submissions
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

        
        try:
            homework = LessonHomework.objects.get(lesson=lesson)
        except LessonHomework.DoesNotExist:
            raise NotFoundError(
                f"Lesson {lesson_id} has no homework",
                code="homework_not_found"
            )

        
        
        from submissions.domain.models import Submission
        submission_count = Submission.objects.filter(
            assignment__lesson_homework_id=homework.id
        ).count()
        if submission_count > 0:
            raise BusinessValidationError(
                code="submissions_exist",
                lang="uz",
                message=f"Cannot remove homework: {submission_count} submissions exist. "
                        "This would orphan student work."
            )

        homework_id = str(homework.id)

        
        homework.delete()