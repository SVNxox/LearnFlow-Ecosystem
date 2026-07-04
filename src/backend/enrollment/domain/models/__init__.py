"""
Enrollment Domain models.

Feature-sliced structure: one file = one model.
"""

from .enrollment import CourseEnrollment
from .access_rule import AccessRule
from .prerequisite import EnrollmentPrerequisite

__all__ = [
    'CourseEnrollment',
    'AccessRule',
    'EnrollmentPrerequisite',
]
