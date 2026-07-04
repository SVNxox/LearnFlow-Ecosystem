"""
Learning Domain models.

Feature-sliced structure: one file = one model (~150 lines).

Exports all models for convenient imports:
    from src.backend.learning.domain.models import Course, Module, Lesson

Note: CourseEnrollment moved to enrollment/ domain (ADR-032, 2026-06-08)
"""

from .base import TimestampedModel, SoftDeleteModel
from .category import CourseCategory
from .course import Course
from .module import Module
from .lesson import Lesson
from .content import LessonContent
from .homework import LessonHomework
from .practice import LessonPractice
from .quiz import LessonQuiz, QuizQuestion, QuizOption

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
