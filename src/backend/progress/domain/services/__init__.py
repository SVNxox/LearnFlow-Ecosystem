"""
Domain Services

Business logic that doesn't naturally fit into a single entity.
Services coordinate multiple entities and enforce domain rules.
"""

from .progress_initialization import ProgressInitializationService
from .lesson_completion import LessonCompletionService
from .completion_cascade import CompletionCascadeService

__all__ = [
    'ProgressInitializationService',
    'LessonCompletionService',
    'CompletionCascadeService',
]
