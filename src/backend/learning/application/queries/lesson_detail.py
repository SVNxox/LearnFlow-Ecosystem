"""
LessonDetailQuery — детальные запросы для уроков.
"""
import logging

from dataclasses import dataclass, field
from typing import Optional

from django.contrib.auth import get_user_model
from django.db.models import Q

from src.backend.learning.domain.models import (
    Lesson,
    LessonContent,
    LessonHomework,
    LessonPractice,
    LessonQuiz,
    QuizQuestion,
)

logger = logging.getLogger(__name__)

User = get_user_model()


@dataclass
class ContentItemDTO:
    """Контент элемент урока — соответствует фронтенд типу ContentItem."""

    id: str
    type: str  
    title: str
    description: str = ''
    url: str = ''
    body: str = ''
    duration_seconds: Optional[int] = None  
    file_size_bytes: Optional[int] = None  
    metadata: dict = field(default_factory=dict)  
    is_required: bool = False  
    is_downloadable: bool = False  
    order: int = 0
    created_at: Optional[str] = None  
    updated_at: Optional[str] = None  


@dataclass
class HomeworkDTO:
    """Homework definition — соответствует фронтенд типу HomeworkInfo."""

    id: str
    title: str
    description: str = ''  
    instructions: str = ''
    max_score: int = 100
    type: str = 'text'  
    submission_types_allowed: list = field(default_factory=list)  
    allowed_file_extensions: str = ''  
    max_file_size_mb: int = 50  
    deadline_offset_days: Optional[int] = None  


@dataclass
class PracticeItemDTO:
    """Practice item DTO — соответствует фронтенд типу PracticeItemInfo."""

    id: str
    title: str
    description: str = ''
    instructions: str = ''
    practice_type: str = 'coding'  
    starter_code: str = ''
    solution_code: str = ''
    language: str = ''
    hints: list = field(default_factory=list)
    max_score: int = 100
    time_limit_minutes: Optional[int] = None
    order: int = 0


@dataclass
class QuizQuestionDTO:
    """Quiz question с опциями."""

    id: str
    question_type: str
    body: str
    explanation: Optional[str] = None
    points: int = 1
    order: int = 0
    options: list = field(default_factory=list)


@dataclass
class QuizDTO:
    """Quiz definition — соответствует фронтенд типу QuizInfo."""

    id: str
    title: str = ''  
    pass_score: int = 70
    max_attempts: Optional[int] = None
    time_limit_minutes: Optional[int] = None
    shuffle_questions: bool = False
    shuffle_options: bool = False
    show_correct_answers: bool = False
    questions: list = field(default_factory=list)


@dataclass
class LessonDetailDTO:
    """Полная информация об уроке."""

    id: str
    title: str
    description: Optional[str]
    order: int
    estimated_minutes: Optional[int]
    is_published: bool
    is_free_preview: bool
    module_id: str
    module_title: str
    course_id: str
    course_title: str
    created_at: Optional[str] = None  
    updated_at: Optional[str] = None  
    content_items: list = field(default_factory=list)
    homework: Optional[HomeworkDTO] = None
    practice_items: list = field(default_factory=list)
    quiz: Optional[QuizDTO] = None


def _can_view_all_content(user: Optional[User], course=None) -> bool:
    """Проверяет права на просмотр всего контента."""
    if not user or not user.is_authenticated:
        return False

    user_roles = []
    if hasattr(user, 'get_roles'):
        try:
            user_roles = user.get_roles()
        except Exception:
            user_roles = []

    is_admin = 'admin' in user_roles
    is_staff = 'staff' in user_roles
    is_course_author = course and course.created_by_id == user.id

    return is_admin or is_staff or bool(is_course_author)


class LessonDetailQuery:
    """Read-only queries для детального просмотра уроков."""

    @staticmethod
    def get_lesson_detail(
        lesson_id: str, user: Optional[User] = None
    ) -> Optional[LessonDetailDTO]:
        """Возвращает полную информацию об уроке."""
        qs = (
            Lesson.objects.filter(id=lesson_id, deleted_at__isnull=True)
            .select_related("module", "module__course")
        )

        try:
            lesson = qs.get()
        except Lesson.DoesNotExist:
            return None

        can_view_all = _can_view_all_content(user, lesson.module.course)

        
        if not can_view_all and not lesson.is_published:
            return None

        
        if not can_view_all and not lesson.is_free_preview:
            if not user:
                return None

            from src.backend.enrollment.domain.models import CourseEnrollment

            has_enrollment = CourseEnrollment.objects.filter(
                user=user,
                course_id=lesson.module.course_id,
                status="active",
            ).exists()

            if not has_enrollment:
                return None

        
        content_items = LessonDetailQuery._get_lesson_content(lesson_id)
        homework = LessonDetailQuery._get_lesson_homework(lesson_id)
        practice_items = LessonDetailQuery._get_lesson_practice(lesson_id)
        quiz = LessonDetailQuery._get_lesson_quiz(lesson_id, can_view_all=can_view_all)

        return LessonDetailDTO(
            id=str(lesson.id),
            title=lesson.title,
            description=lesson.description,
            order=lesson.order,
            estimated_minutes=lesson.estimated_minutes,
            is_published=lesson.is_published,
            is_free_preview=lesson.is_free_preview,
            module_id=str(lesson.module.id),
            module_title=lesson.module.title,
            course_id=str(lesson.module.course_id),
            course_title=lesson.module.course.title,
            created_at=lesson.created_at.isoformat() if lesson.created_at else None,
            updated_at=lesson.updated_at.isoformat() if lesson.updated_at else None,
            content_items=content_items,
            homework=homework,
            practice_items=practice_items,
            quiz=quiz,
        )

    @staticmethod
    def _get_lesson_content(lesson_id: str) -> list[ContentItemDTO]:
        """Загружает контент элементы урока."""
        
        content_items = LessonContent.objects.filter(
            lesson_id=lesson_id
        ).order_by("order")

        return [
            ContentItemDTO(
                id=str(item.id),
                type=item.type,
                title=item.title or '',
                description=item.description or '',
                url=item.url or '',
                body=item.body or '',
                duration_seconds=item.duration_seconds,
                file_size_bytes=item.file_size_bytes,
                metadata=item.metadata or {},
                is_required=item.is_required,
                is_downloadable=item.is_downloadable,
                order=item.order,
                created_at=item.created_at.isoformat() if item.created_at else None,
                updated_at=item.updated_at.isoformat() if item.updated_at else None,
            )
            for item in content_items
        ]

    @staticmethod
    def _get_lesson_homework(lesson_id: str) -> Optional[HomeworkDTO]:
        """Загружает homework definition."""
        try:
            
            homework = LessonHomework.objects.get(lesson_id=lesson_id)

            logger.info(f"Found homework for lesson {lesson_id}: {homework.title}")

            return HomeworkDTO(
                id=str(homework.id),
                title=homework.title,
                description=homework.description or '',
                instructions=homework.instructions or '',
                max_score=homework.max_score,
                type=homework.submission_type,  
                submission_types_allowed=homework.allowed_file_types or [],  
                allowed_file_extensions='',  
                max_file_size_mb=homework.max_file_size_mb or 50,
                deadline_offset_days=homework.deadline_offset_days,
            )
        except LessonHomework.DoesNotExist:
            logger.info(f"No homework found for lesson {lesson_id}")
            return None
        except Exception as e:
            logger.error(f"Error getting homework for lesson {lesson_id}: {e}", exc_info=True)
            return None

    @staticmethod
    def _get_lesson_practice(lesson_id: str) -> list[PracticeItemDTO]:
        """Загружает practice items."""
        
        practice_qs = LessonPractice.objects.filter(lesson_id=lesson_id)

        
        if hasattr(LessonPractice, 'deleted_at'):
            practice_qs = practice_qs.filter(deleted_at__isnull=True)

        practice_items = practice_qs.order_by("order")

        return [
            PracticeItemDTO(
                id=str(item.id),
                title=item.title,
                description=item.description or '',
                instructions=item.instructions or '',
                practice_type=getattr(item, 'practice_type', 'coding'),
                starter_code=item.starter_code or '',
                solution_code=item.solution_code or '',
                language=item.language or '',
                hints=item.hints or [],
                max_score=item.max_score,
                time_limit_minutes=item.time_limit_minutes,
                order=item.order,
            )
            for item in practice_items
        ]

    @staticmethod
    def _get_lesson_quiz(lesson_id: str, can_view_all: bool = False) -> Optional[QuizDTO]:
        """Загружает quiz с вопросами и опциями."""
        try:
            
            quiz_qs = LessonQuiz.objects.filter(lesson_id=lesson_id)
            if hasattr(LessonQuiz, 'deleted_at'):
                quiz_qs = quiz_qs.filter(deleted_at__isnull=True)
            quiz = quiz_qs.first()

            if not quiz:
                return None
        except LessonQuiz.DoesNotExist:
            return None

        
        questions_qs = QuizQuestion.objects.filter(quiz_id=quiz.id)
        if hasattr(QuizQuestion, 'deleted_at'):
            questions_qs = questions_qs.filter(deleted_at__isnull=True)

        questions = questions_qs.prefetch_related("options").order_by("order")

        questions_data = []
        for question in questions:
            options_data = [
                {
                    "id": str(option.id),
                    "body": option.body,
                    "is_correct": option.is_correct if can_view_all else None,
                }
                for option in question.options.order_by("order")
            ]

            questions_data.append(
                QuizQuestionDTO(
                    id=str(question.id),
                    question_type=question.question_type,
                    body=question.body,
                    explanation=question.explanation,
                    points=question.points,
                    order=question.order,
                    options=options_data,
                )
            )

        return QuizDTO(
            id=str(quiz.id),
            title=quiz.title,
            pass_score=quiz.pass_score,
            max_attempts=quiz.max_attempts,
            time_limit_minutes=quiz.time_limit_minutes,
            shuffle_questions=getattr(quiz, 'shuffle_questions', False),
            shuffle_options=getattr(quiz, 'shuffle_options', False),
            show_correct_answers=getattr(quiz, 'show_correct_answers', False),
            questions=questions_data,
        )