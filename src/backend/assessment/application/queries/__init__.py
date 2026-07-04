"""
Assessment Application Queries

Queries return read-only data from the domain.
Following CQRS pattern: Queries = Read operations.
"""

from .get_attempt_detail import GetAttemptDetailQuery, AttemptDetailResult, AttemptItemResult
from .get_student_attempts import GetStudentAttemptsQuery, StudentAttemptsResult, AttemptSummary
from .get_pending_reviews import GetPendingReviewsQuery, PendingReviewsResult, PendingReviewItem

__all__ = [
    'GetAttemptDetailQuery',
    'AttemptDetailResult',
    'AttemptItemResult',
    'GetStudentAttemptsQuery',
    'StudentAttemptsResult',
    'AttemptSummary',
    'GetPendingReviewsQuery',
    'PendingReviewsResult',
    'PendingReviewItem',
]
