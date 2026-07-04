"""
ManageQuizCommand — управление квизами урока.

Business Rules:
- Только один quiz на урок
- pass_score: 0-100
- single_choice: ровно 1 correct option
- multiple_choice: ≥2 options, ≥1 correct
- Question type immutable
- Hard delete quiz удаляет всё (cascade)

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
from src.backend.learning.domain.models import (
    Lesson,
    LessonQuiz,
    QuizQuestion,
    QuizOption,
)

User = get_user_model()


@dataclass
class CreateQuizData:
    """Input data для создания quiz."""

    pass_score: int = 70  
    max_attempts: Optional[int] = None  
    time_limit_minutes: Optional[int] = None
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_correct_answers: bool = True


@dataclass
class UpdateQuizSettingsData:
    """Input data для обновления quiz settings."""

    pass_score: Optional[int] = None
    max_attempts: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    show_correct_answers: Optional[bool] = None


@dataclass
class AddQuestionData:
    """Input data для добавления вопроса."""

    question_type: str  
    body: str
    explanation: Optional[str] = None
    points: int = 1


@dataclass
class UpdateQuestionData:
    """Input data для обновления вопроса."""

    body: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[int] = None


@dataclass
class AddOptionData:
    """Input data для добавления опции."""

    body: str
    is_correct: bool = False


def _check_lesson_permission(actor: User, lesson: Lesson) -> None:
    """
    Проверяет права на управление контентом урока (quiz/homework/practice).

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
            "Only admin, staff, or course author can manage quiz",
            code="insufficient_permissions"
        )


def _check_quiz_permission(actor: User, quiz: LessonQuiz) -> None:
    """Проверяет права через quiz → lesson."""
    _check_lesson_permission(actor, quiz.lesson)


def _check_question_permission(actor: User, question: QuizQuestion) -> None:
    """Проверяет права через question → quiz → lesson."""
    _check_lesson_permission(actor, question.quiz.lesson)


class ManageQuizCommand:
    """
    Command для управления quiz урока.

    Permissions: Admin, Staff, or Course Author
    """

    ALLOWED_QUESTION_TYPES = ['single_choice', 'multiple_choice']

    @staticmethod
    @transaction.atomic
    def create_quiz(lesson_id: str, data: CreateQuizData, actor: User) -> LessonQuiz:
        """
        Создаёт quiz для урока.

        Business Rule: Только один quiz на урок.

        Raises:
            NotFoundError: если урок не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если quiz уже существует или данные невалидны
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

        
        if LessonQuiz.objects.filter(lesson=lesson).exists():
            raise BusinessValidationError(
                code="quiz_already_exists",
                lang="uz",
                message=f"Lesson {lesson_id} already has a quiz"
            )

        
        if not (0 <= data.pass_score <= 100):
            raise BusinessValidationError(
                code="invalid_pass_score",
                lang="uz",
                message="Pass score must be between 0 and 100"
            )

        
        if data.max_attempts is not None and data.max_attempts <= 0:
            raise BusinessValidationError(
                code="invalid_max_attempts",
                lang="uz",
                message="Max attempts must be greater than 0"
            )

        
        if data.time_limit_minutes is not None and data.time_limit_minutes <= 0:
            raise BusinessValidationError(
                code="invalid_time_limit",
                lang="uz",
                message="Time limit must be greater than 0"
            )

        
        quiz = LessonQuiz.objects.create(
            lesson=lesson,
            pass_score=data.pass_score,
            max_attempts=data.max_attempts,
            time_limit_minutes=data.time_limit_minutes,
            shuffle_questions=data.shuffle_questions,
            shuffle_options=data.shuffle_options,
            show_correct_answers=data.show_correct_answers,
        )

        return quiz

    @staticmethod
    @transaction.atomic
    def update_quiz_settings(
        quiz_id: str, data: UpdateQuizSettingsData, actor: User
    ) -> LessonQuiz:
        """
        Обновляет настройки quiz.

        Raises:
            NotFoundError: если quiz не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            quiz = (
                LessonQuiz.objects.select_for_update()
                .select_related("lesson__module__course")
                .get(id=quiz_id)
            )
        except LessonQuiz.DoesNotExist:
            raise NotFoundError(f"Quiz {quiz_id} not found", code="quiz_not_found")

        
        _check_quiz_permission(actor, quiz)

        
        update_fields = []

        if data.pass_score is not None:
            if not (0 <= data.pass_score <= 100):
                raise BusinessValidationError(
                    code="invalid_pass_score",
                    lang="uz",
                    message="Pass score must be between 0 and 100"
                )
            quiz.pass_score = data.pass_score
            update_fields.append("pass_score")

        if data.max_attempts is not None:
            if data.max_attempts <= 0:
                raise BusinessValidationError(
                    code="invalid_max_attempts",
                    lang="uz",
                    message="Max attempts must be greater than 0"
                )
            quiz.max_attempts = data.max_attempts
            update_fields.append("max_attempts")

        if data.time_limit_minutes is not None:
            if data.time_limit_minutes <= 0:
                raise BusinessValidationError(
                    code="invalid_time_limit",
                    lang="uz",
                    message="Time limit must be greater than 0"
                )
            quiz.time_limit_minutes = data.time_limit_minutes
            update_fields.append("time_limit_minutes")

        if data.shuffle_questions is not None:
            quiz.shuffle_questions = data.shuffle_questions
            update_fields.append("shuffle_questions")

        if data.shuffle_options is not None:
            quiz.shuffle_options = data.shuffle_options
            update_fields.append("shuffle_options")

        if data.show_correct_answers is not None:
            quiz.show_correct_answers = data.show_correct_answers
            update_fields.append("show_correct_answers")

        
        if update_fields:
            quiz.save(update_fields=update_fields)

        return quiz

    @staticmethod
    @transaction.atomic
    def add_question(quiz_id: str, data: AddQuestionData, actor: User) -> QuizQuestion:
        """
        Добавляет вопрос в quiz (appends to end).

        Raises:
            NotFoundError: если quiz не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            quiz = (
                LessonQuiz.objects.select_for_update()
                .select_related("lesson__module__course")
                .get(id=quiz_id)
            )
        except LessonQuiz.DoesNotExist:
            raise NotFoundError(f"Quiz {quiz_id} not found", code="quiz_not_found")

        
        _check_quiz_permission(actor, quiz)

        
        if data.question_type not in ManageQuizCommand.ALLOWED_QUESTION_TYPES:
            allowed = ", ".join(ManageQuizCommand.ALLOWED_QUESTION_TYPES)
            raise BusinessValidationError(
                code="invalid_question_type",
                lang="uz",
                message=f"Invalid question type '{data.question_type}'. Allowed: {allowed}"
            )

        
        clean_body = data.body.strip()
        if len(clean_body) < 5:
            raise BusinessValidationError(
                code="body_too_short",
                lang="uz",
                message="Question body must be at least 5 characters"
            )

        
        if data.points <= 0:
            raise BusinessValidationError(
                code="invalid_points",
                lang="uz",
                message="Points must be greater than 0"
            )

        
        max_order = (
            QuizQuestion.objects.filter(quiz_id=quiz_id).aggregate(
                max_order=Max("order")
            )["max_order"]
            or 0
        )

        
        question = QuizQuestion.objects.create(
            quiz=quiz,
            question_type=data.question_type,
            body=clean_body,
            explanation=data.explanation,
            points=data.points,
            order=max_order + 1,
        )

        return question

    @staticmethod
    @transaction.atomic
    def update_question(
        question_id: str, data: UpdateQuestionData, actor: User
    ) -> QuizQuestion:
        """
        Обновляет вопрос.

        Note: question_type immutable.

        Raises:
            NotFoundError: если вопрос не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны
        """
        
        try:
            question = (
                QuizQuestion.objects.select_for_update()
                .select_related("quiz__lesson__module__course")
                .get(id=question_id)
            )
        except QuizQuestion.DoesNotExist:
            raise NotFoundError(f"Question {question_id} not found", code="question_not_found")

        
        _check_question_permission(actor, question)

        
        update_fields = []

        if data.body is not None:
            clean_body = data.body.strip()
            if len(clean_body) < 5:
                raise BusinessValidationError(
                    code="body_too_short",
                    lang="uz",
                    message="Question body must be at least 5 characters"
                )
            question.body = clean_body
            update_fields.append("body")

        if data.explanation is not None:
            question.explanation = data.explanation
            update_fields.append("explanation")

        if data.points is not None:
            if data.points <= 0:
                raise BusinessValidationError(
                    code="invalid_points",
                    lang="uz",
                    message="Points must be greater than 0"
                )
            question.points = data.points
            update_fields.append("points")

        
        if update_fields:
            question.save(update_fields=update_fields)

        return question

    @staticmethod
    @transaction.atomic
    def add_option(question_id: str, data: AddOptionData, actor: User) -> QuizOption:
        """
        Добавляет опцию к вопросу (appends to end).

        Business Rules:
        - single_choice: ровно 1 correct option
        - multiple_choice: ≥2 options, ≥1 correct

        Raises:
            NotFoundError: если вопрос не найден
            AccessDeniedError: если actor не имеет прав
            BusinessValidationError: если данные невалидны или нарушены правила
        """
        
        try:
            question = (
                QuizQuestion.objects.select_for_update()
                .select_related("quiz__lesson__module__course")
                .prefetch_related("options")
                .get(id=question_id)
            )
        except QuizQuestion.DoesNotExist:
            raise NotFoundError(f"Question {question_id} not found", code="question_not_found")

        
        _check_question_permission(actor, question)

        
        clean_body = data.body.strip()
        if len(clean_body) < 1:
            raise BusinessValidationError(
                code="option_body_empty",
                lang="uz",
                message="Option body must not be empty"
            )

        
        if question.question_type == "single_choice":
            existing_correct = question.options.filter(is_correct=True).count()
            if data.is_correct and existing_correct >= 1:
                raise BusinessValidationError(
                    code="single_choice_constraint",
                    lang="uz",
                    message="Single choice question can have only one correct option"
                )

        
        max_order = (
            QuizOption.objects.filter(question_id=question_id).aggregate(
                max_order=Max("order")
            )["max_order"]
            or 0
        )

        
        option = QuizOption.objects.create(
            question=question,
            body=clean_body,
            is_correct=data.is_correct,
            order=max_order + 1,
        )

        return option

    @staticmethod
    @transaction.atomic
    def delete_quiz(quiz_id: str, actor: User) -> None:
        """
        Удаляет quiz (hard delete, cascades to questions and options).

        Raises:
            NotFoundError: если quiz не найден
            AccessDeniedError: если actor не имеет прав
        """
        
        try:
            quiz = LessonQuiz.objects.select_related("lesson__module__course").get(
                id=quiz_id
            )
        except LessonQuiz.DoesNotExist:
            raise NotFoundError(f"Quiz {quiz_id} not found", code="quiz_not_found")

        
        _check_quiz_permission(actor, quiz)

        lesson_id = str(quiz.lesson_id)

        
        quiz.delete()