"""
Submissions Domain Models

Feature-Sliced Architecture (ADR-033):
- One file per model (~100-150 lines)
- Explicit imports, no implicit coupling
"""

from .assignment import Assignment
from .submission import Submission
from .revision import SubmissionRevision
from .file import SubmissionFile
from .auto_check import AutoCheck
from .review import SubmissionReview

__all__ = [
    'Assignment',
    'Submission',
    'SubmissionRevision',
    'SubmissionFile',
    'AutoCheck',
    'SubmissionReview',
]
