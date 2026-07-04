"""
Request Changes Command

Mentor requests changes to submission.
"""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction

from src.backend.submissions.domain.models import SubmissionReview, Submission
from src.backend.submissions.domain.services.review_service import ReviewService


@dataclass
class RequestChangesCommand:
    """
    Mentor requests changes to submission.

    Called by: Mentor when reviewing submission
    """
    submission_id: UUID
    revision_id: UUID
    mentor_id: UUID
    score: Decimal
    feedback: str


class RequestChangesHandler:
    """
    Handler for RequestChangesCommand.

    Validation:
    - Submission must be in under_review status
    - Mentor must be authorized (checked in presentation layer)
    - Score must be between 0 and max_score

    Events emitted:
    - SubmissionChangesRequested (Signal) → Student notification
    """

    @staticmethod
    @transaction.atomic
    def handle(command: RequestChangesCommand) -> SubmissionReview:
        
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
            status=SubmissionReview.ReviewStatus.CHANGES_REQUESTED
        )

        
        transaction.on_commit(lambda: _emit_changes_requested_event(review))

        return review


def _emit_changes_requested_event(review: SubmissionReview):
    """
    Emit SubmissionChangesRequested event.

    TODO: Implement after event handlers task.
    """
    pass
