"""
Approve Submission Command

Mentor approves submission.
"""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from src.backend.submissions.domain.models import SubmissionReview, Submission
from src.backend.submissions.domain.services.review_service import ReviewService


@dataclass
class ApproveSubmissionCommand:
    """
    Mentor approves submission.

    Called by: Mentor when submission meets requirements
    """
    submission_id: UUID
    revision_id: UUID
    mentor_id: UUID
    score: Decimal
    feedback: str


class ApproveSubmissionHandler:
    """
    Handler for ApproveSubmissionCommand.

    Validation:
    - Submission must be in under_review status
    - Mentor must be authorized (checked in presentation layer)
    - Score must be between 0 and max_score

    Events emitted:
    - SubmissionReviewed (Outbox) → Assessment (update response points)
    - SubmissionApproved (Signal) → UserProgress (homework gate)
    """

    @staticmethod
    @transaction.atomic
    def handle(command: ApproveSubmissionCommand) -> SubmissionReview:
        
        submission = Submission.objects.select_for_update().get(id=command.submission_id)

        if submission.status != Submission.SubmissionStatus.UNDER_REVIEW:
            
            if submission.status == Submission.SubmissionStatus.SUBMITTED:
                submission.status = Submission.SubmissionStatus.UNDER_REVIEW
                submission.save()
            else:
                raise ValueError(f"Cannot review from status {submission.status}")

        
        review = ReviewService.submit_review(
            submission_id=command.submission_id,
            revision_id=command.revision_id,
            mentor_id=command.mentor_id,
            score=command.score,
            feedback=command.feedback,
            status=SubmissionReview.ReviewStatus.APPROVED
        )

        
        transaction.on_commit(lambda: _emit_approved_events(review))

        return review


def _emit_approved_events(review: SubmissionReview):
    """
    Emit SubmissionApproved and SubmissionReviewed events.

    TODO: Implement after event handlers task.
    """
    pass
