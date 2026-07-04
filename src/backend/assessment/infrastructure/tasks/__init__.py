"""
Assessment Infrastructure Tasks

Celery tasks for background processing.
"""

from .coding_execution import execute_coding_task

__all__ = [
    'execute_coding_task',
]
