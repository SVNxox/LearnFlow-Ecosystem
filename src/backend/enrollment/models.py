"""
Enrollment Domain models — Feature-Sliced Architecture.

All models have been moved to enrollment/domain/models/ directory.
This file re-exports them for backward compatibility with Django's app loading.
"""

from src.backend.enrollment.domain.models import CourseEnrollment

__all__ = [
    'CourseEnrollment',
]
