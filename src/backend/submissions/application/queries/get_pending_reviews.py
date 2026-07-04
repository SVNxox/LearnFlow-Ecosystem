"""
Get Pending Reviews Query

Mentor work queue - submissions waiting for review.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.backend.submissions.domain.models import Submission


@dataclass
class PendingReviewDTO:
    """Data Transfer Object for pending review."""
    id: UUID
    assignment_id: UUID
    assignment_title: str
    assignment_type: str
    assignment_max_score: Decimal
    student_id: UUID
    enrollment_id: UUID
    status: str
    current_revision_number: int
    last_submitted_at: str
    deadline: Optional[str]
    is_overdue: bool
    waiting_days: int  


class GetPendingReviewsQuery:
    """
    Get submissions waiting for mentor review.

    Called by: Mentor
    """

    @staticmethod
    def execute(
        mentor_id: Optional[UUID] = None,
        limit: int = 50
    ) -> list[PendingReviewDTO]:
        """
        Retrieve submissions pending review.

        Filters:
        - status IN (submitted, under_review)
        - Optionally by mentor's groups (TODO: when Mentorship Domain ready)

        Ordered by: last_submitted_at ASC (oldest first)
        """
        from django.utils import timezone
        from datetime import timedelta

        queryset = Submission.objects.filter(
            status__in=[
                Submission.SubmissionStatus.SUBMITTED,
                Submission.SubmissionStatus.UNDER_REVIEW
            ]
        ).select_related('assignment').order_by('last_submitted_at')

        
        
        
        
        

        submissions = queryset[:limit]

        now = timezone.now()
        result = []

        for s in submissions:
            waiting_days = 0
            if s.last_submitted_at:
                delta = now - s.last_submitted_at
                waiting_days = delta.days

            result.append(
                PendingReviewDTO(
                    id=s.id,
                    assignment_id=s.assignment.id,
                    assignment_title=s.assignment.title,
                    assignment_type=s.assignment.type,
                    assignment_max_score=s.assignment.max_score,
                    student_id=s.student_id,
                    enrollment_id=s.enrollment_id,
                    status=s.status,
                    current_revision_number=s.current_revision_number,
                    last_submitted_at=s.last_submitted_at.isoformat() if s.last_submitted_at else "",
                    deadline=s.deadline.isoformat() if s.deadline else None,
                    is_overdue=s.is_overdue,
                    waiting_days=waiting_days
                )
            )

        return result
