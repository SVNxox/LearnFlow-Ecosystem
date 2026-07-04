"""
Learning Domain models — Feature-Sliced Architecture.

All models have been moved to learning/domain/models/ directory.
This file re-exports them for backward compatibility with Django's app loading.

Note: CourseEnrollment moved to enrollment/ domain (ADR-032, 2026-06-08)
"""

from src.backend.learning.domain.models import (
    TimestampedModel,
    SoftDeleteModel,
    CourseCategory,
    Course,
    Module,
    Lesson,
    LessonContent,
    LessonHomework,
    LessonPractice,
    LessonQuiz,
    QuizQuestion,
    QuizOption,
)

__all__ = [
    'TimestampedModel',
    'SoftDeleteModel',
    'CourseCategory',
    'Course',
    'Module',
    'Lesson',
    'LessonContent',
    'LessonHomework',
    'LessonPractice',
    'LessonQuiz',
    'QuizQuestion',
    'QuizOption',
]
