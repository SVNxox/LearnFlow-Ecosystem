"""
Application Queries

Queries return read-only data from the domain.
Following CQRS pattern: Queries = Read operations.
"""

from .get_next_action import GetNextActionQuery, NextActionResult
from .get_progress_dashboard import (
    GetProgressDashboardQuery,
    GetProgressDashboardHandler,
    ProgressDashboardResult,
    CourseProgressSummary,
)
from .get_course_progress_detail import (
    GetCourseProgressDetailQuery,
    CourseProgressDetailResult,
    ModuleProgressDetail,
    LessonProgressDetail,
)

__all__ = [
    'GetNextActionQuery',
    'NextActionResult',
    'GetProgressDashboardQuery',
    'GetProgressDashboardHandler',
    'ProgressDashboardResult',
    'CourseProgressSummary',
    'GetCourseProgressDetailQuery',
    'CourseProgressDetailResult',
    'ModuleProgressDetail',
    'LessonProgressDetail',
]
