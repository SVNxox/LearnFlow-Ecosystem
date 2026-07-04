"""
UserProgress Domain Models Export

Django requires models.py at app root level.
This file re-exports models from domain/models/ package.

Feature-Sliced Architecture: actual models live in domain/models/*.py
"""

from .domain.models import (
    CourseProgress,
    ModuleProgress,
    LessonProgress,
    LessonContentView,
)

__all__ = [
    'CourseProgress',
    'ModuleProgress',
    'LessonProgress',
    'LessonContentView',
]
