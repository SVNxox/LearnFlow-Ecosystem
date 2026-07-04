"""
Get Attempt Detail Query

Returns detailed information about an assessment attempt.
"""
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from src.backend.assessment.domain.models import (
    AssessmentAttempt,
    AssessmentResponse,
)


@dataclass
class ItemOption:
    """Option for choice-type items."""
    id: UUID
    text: str
    order: int


@dataclass
class AttemptItemResult:
    """Result for a single item in the attempt."""
    item_id: UUID
    item_type: str
    item_title: str
    order: int
    max_points: Decimal

    options: Optional[List[ItemOption]]

    selected_option_ids: List[UUID]
    text_response: str
    submitted_code: str

    is_graded: bool
    auto_points: Optional[Decimal]
    mentor_points: Optional[Decimal]
    final_points: Optional[Decimal]
    is_correct: Optional[bool]

    reviewed_by_id: Optional[UUID]
    reviewed_at: Optional[datetime]
    review_comment: str


@dataclass
class AttemptDetailResult:
    """Full attempt details with all responses."""
    attempt_id: UUID
    assessment_id: UUID
    assessment_title: str
    user_id: UUID
    attempt_number: int

    grading_status: str
    started_at: datetime
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_expired: bool

    max_score: Decimal
    final_score: Optional[Decimal]
    percentage: Optional[Decimal]
    passed: Optional[bool]
    passing_percentage: Decimal

    items: List[AttemptItemResult]

    total_items: int
    graded_items: int
    mentor_note: str


class GetAttemptDetailQuery:
    """Query to get full attempt details."""

    def __init__(self, attempt_id: UUID):
        self.attempt_id = attempt_id

    def execute(self) -> AttemptDetailResult:
        """
        Execute query.

        Returns:
            AttemptDetailResult with all data
        """
        attempt = AssessmentAttempt.objects.select_related('assessment').get(
            id=self.attempt_id
        )

        responses = AssessmentResponse.objects.filter(
            attempt=attempt
        ).select_related('item').prefetch_related('item__options').order_by('item__order')

        items = []
        for response in responses:
            options = None
            if response.item.type in ['single_choice', 'multiple_choice']:
                options = [
                    ItemOption(
                        id=opt.id,
                        text=opt.text,
                        order=opt.order
                    )
                    for opt in response.item.options.all()
                ]

            items.append(AttemptItemResult(
                item_id=response.item.id,
                item_type=response.item.type,
                item_title=response.item.title,
                order=response.item.order,
                max_points=response.item.max_points,
                options=options,
                selected_option_ids=response.selected_option_ids or [],
                text_response=response.text_response,
                submitted_code=response.submitted_code,
                is_graded=response.is_graded,
                auto_points=response.auto_points,
                mentor_points=response.mentor_points,
                final_points=response.final_points,
                is_correct=response.is_correct,
                reviewed_by_id=response.reviewed_by_id,
                reviewed_at=response.reviewed_at,
                review_comment=response.review_comment,
            ))

        graded_count = sum(1 for item in items if item.is_graded)

        return AttemptDetailResult(
            attempt_id=attempt.id,
            assessment_id=attempt.assessment.id,
            assessment_title=attempt.assessment.title,
            user_id=attempt.user_id,
            attempt_number=attempt.attempt_number,
            grading_status=attempt.grading_status,
            started_at=attempt.started_at,
            submitted_at=attempt.submitted_at,
            graded_at=attempt.graded_at,
            expires_at=attempt.expires_at,
            is_expired=attempt.is_expired(),
            max_score=attempt.max_score,
            final_score=attempt.final_score,
            percentage=attempt.percentage,
            passed=attempt.passed,
            passing_percentage=attempt.assessment.passing_percentage,
            items=items,
            total_items=len(items),
            graded_items=graded_count,
            mentor_note=attempt.mentor_note,
        )
