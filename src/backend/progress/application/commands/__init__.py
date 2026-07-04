"""
Application Commands

Commands trigger state changes in the domain.
Following CQRS pattern: Commands = Write operations.
"""

from .initialize_progress import InitializeProgressCommand
from .record_content_view import RecordContentViewCommand
from .mark_lesson_completed import MarkLessonCompletedCommand

__all__ = [
    'InitializeProgressCommand',
    'RecordContentViewCommand',
    'MarkLessonCompletedCommand',
]
