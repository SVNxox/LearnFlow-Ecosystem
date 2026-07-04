"""
Submissions Domain Models Re-export

Django requires models to be importable from app.models.
"""

from src.backend.submissions.domain.models import (
    Assignment,
    Submission,
    SubmissionRevision,
    SubmissionFile,
    AutoCheck,
    SubmissionReview,
)

__all__ = [
    'Assignment',
    'Submission',
    'SubmissionRevision',
    'SubmissionFile',
    'AutoCheck',
    'SubmissionReview',
]
