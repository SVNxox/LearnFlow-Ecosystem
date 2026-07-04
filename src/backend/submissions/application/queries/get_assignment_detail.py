"""
Get Assignment Detail Query

Retrieve assignment details with statistics.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.db.models import Count, Avg, Q

from src.backend.submissions.domain.models import Assignment, Submission


@dataclass
class AssignmentDetailDTO:
    """Data Transfer Object for Assignment Detail."""
    id: UUID
    lesson_id: Optional[UUID]
    assessment_item_id: Optional[UUID]
    type: str
    title: str
    description: str
    max_score: Decimal
    deadline_offset_days: Optional[int]
    submission_types_allowed: list[str]
    allowed_file_extensions: Optional[str]
    max_file_size_mb: int
    auto_check_enabled: bool
    auto_check_config: dict
    created_by_id: UUID
    created_at: str
    updated_at: str

    
    total_submissions: int
    pending_reviews: int
    approved_count: int
    average_score: Optional[Decimal]


class GetAssignmentDetailQuery:
    """
    Get assignment detail with statistics.

    Called by: Staff, Mentor
    """

    @staticmethod
    def execute(assignment_id: UUID) -> AssignmentDetailDTO:
        """
        Retrieve assignment with submission statistics.

        Includes:
        - Total submissions
        - Pending reviews (submitted + under_review)
        - Approved count
        - Average score
        """
        assignment = Assignment.objects.annotate(
            total_submissions=Count('submissions', distinct=True),
            pending_reviews=Count(
                'submissions',
                filter=Q(
                    submissions__status__in=[
                        Submission.SubmissionStatus.SUBMITTED,
                        Submission.SubmissionStatus.UNDER_REVIEW
                    ]
                ),
                distinct=True
            ),
            approved_count=Count(
                'submissions',
                filter=Q(submissions__status=Submission.SubmissionStatus.APPROVED),
                distinct=True
            ),
            avg_score=Avg(
                'submissions__final_score',
                filter=Q(submissions__status=Submission.SubmissionStatus.APPROVED)
            )
        ).get(id=assignment_id)

        return AssignmentDetailDTO(
            id=assignment.id,
            lesson_id=assignment.lesson_id,
            assessment_item_id=assignment.assessment_item_id,
            type=assignment.type,
            title=assignment.title,
            description=assignment.description,
            max_score=assignment.max_score,
            deadline_offset_days=assignment.deadline_offset_days,
            submission_types_allowed=assignment.submission_types_allowed,
            allowed_file_extensions=assignment.allowed_file_extensions,
            max_file_size_mb=assignment.max_file_size_mb,
            auto_check_enabled=assignment.auto_check_enabled,
            auto_check_config=assignment.auto_check_config or {},
            created_by_id=assignment.created_by_id,
            created_at=assignment.created_at.isoformat(),
            updated_at=assignment.updated_at.isoformat(),
            total_submissions=assignment.total_submissions,
            pending_reviews=assignment.pending_reviews,
            approved_count=assignment.approved_count,
            average_score=assignment.avg_score
        )
