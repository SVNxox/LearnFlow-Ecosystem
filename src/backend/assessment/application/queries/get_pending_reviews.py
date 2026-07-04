"""
Get Pending Reviews Query

Returns list of responses waiting for mentor review.
"""
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.backend.assessment.domain.models import (
    AssessmentAttempt,
    AssessmentResponse,
)


@dataclass
class PendingReviewItem:
    """Single response waiting for review."""
    response_id: UUID
    attempt_id: UUID
    assessment_id: UUID
    assessment_title: str
    user_id: UUID
    item_id: UUID
    item_type: str
    item_title: str
    max_points: float

    
    text_response: str
    submitted_code: str
    coding_language: str

    
    submitted_at: Optional[datetime]
    started_at: datetime


@dataclass
class PendingReviewsResult:
    """List of pending reviews."""
    items: List[PendingReviewItem]
    total_count: int


class GetPendingReviewsQuery:
    """
    Query to get responses waiting for mentor review.

    Filters:
    - attempt.grading_status = mentor_review OR auto_graded
    - response.is_graded = False
    - item.mentor_review_required = True
    """

    def __init__(self, mentor_id: Optional[UUID] = None, limit: int = 50):
        self.mentor_id = mentor_id
        self.limit = limit

    def execute(self) -> PendingReviewsResult:
        """
        Execute query.

        Returns:
            PendingReviewsResult with pending items
        """
        attempts = AssessmentAttempt.objects.filter(
            grading_status__in=[
                AssessmentAttempt.GradingStatus.MENTOR_REVIEW,
                AssessmentAttempt.GradingStatus.AUTO_GRADED,
            ]
        ).select_related('assessment')

        pending_items = []

        for attempt in attempts[:self.limit]:
            responses = AssessmentResponse.objects.filter(
                attempt=attempt,
                is_graded=False,
                item__mentor_review_required=True
            ).select_related('item')

            for response in responses:
                pending_items.append(PendingReviewItem(
                    response_id=response.id,
                    attempt_id=attempt.id,
                    assessment_id=attempt.assessment.id,
                    assessment_title=attempt.assessment.title,
                    user_id=attempt.user_id,
                    item_id=response.item.id,
                    item_type=response.item.type,
                    item_title=response.item.title,
                    max_points=float(response.item.max_points),
                    text_response=response.text_response,
                    submitted_code=response.submitted_code,
                    coding_language=response.coding_language,
                    submitted_at=attempt.submitted_at,
                    started_at=attempt.started_at,
                ))

        return PendingReviewsResult(
            items=pending_items,
            total_count=len(pending_items)
        )
