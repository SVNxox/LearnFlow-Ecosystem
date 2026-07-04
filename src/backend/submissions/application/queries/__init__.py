"""
Submissions Application Layer — Queries

All query handlers for Submissions Domain.
"""
from .get_assignment_detail import GetAssignmentDetailQuery, AssignmentDetailDTO
from .get_my_submissions import GetMySubmissionsQuery, MySubmissionDTO
from .get_submission_detail import GetSubmissionDetailQuery, SubmissionDetailDTO
from .get_pending_reviews import GetPendingReviewsQuery, PendingReviewDTO
from .get_submission_history import GetSubmissionHistoryQuery, SubmissionEventDTO

__all__ = [
    'GetAssignmentDetailQuery',
    'AssignmentDetailDTO',
    'GetMySubmissionsQuery',
    'MySubmissionDTO',
    'GetSubmissionDetailQuery',
    'SubmissionDetailDTO',
    'GetPendingReviewsQuery',
    'PendingReviewDTO',
    'GetSubmissionHistoryQuery',
    'SubmissionEventDTO',
]
