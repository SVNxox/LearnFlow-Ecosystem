"""
Review Service

Handles mentor review of submissions.
"""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from src.backend.submissions.domain.models import (
    Submission,
    SubmissionRevision,
    SubmissionReview,
)


class ReviewService:
    """
    Review Service — проверка ментора.

    Flow:
    1. Mentor reviews revision
    2. Mentor submits review (score, feedback, status)
    3. Submission status updated based on review status
    """

    @staticmethod
    @transaction.atomic
    def submit_review(
        submission_id: UUID,
        revision_id: UUID,
        mentor_id: UUID,
        score: Decimal,
        feedback: str,
        status: str
    ) -> SubmissionReview:
        """
        Submit mentor review.

        Status transitions based on review.status:
        - changes_requested → submission.status = changes_requested
        - approved → submission.status = approved
        - rejected → submission.status = rejected
        """
        submission = Submission.objects.select_for_update().get(id=submission_id)
        revision = SubmissionRevision.objects.get(id=revision_id)

        
        if submission.status != Submission.SubmissionStatus.UNDER_REVIEW:
            raise ValueError(f"Cannot review from status {submission.status}")

        if revision.submission_id != submission.id:
            raise ValueError("Revision does not belong to this submission")

        
        if score < Decimal('0.00') or score > submission.assignment.max_score:
            raise ValueError(f"Score must be between 0 and {submission.assignment.max_score}")

        
        existing = SubmissionReview.objects.filter(
            submission=submission,
            revision=revision
        ).first()

        if existing:
            raise ValueError("This revision has already been reviewed")

        
        review = SubmissionReview.objects.create(
            submission=submission,
            revision=revision,
            mentor_id=mentor_id,
            score=score,
            max_score=submission.assignment.max_score,
            feedback=feedback,
            status=status
        )

        
        if status == SubmissionReview.ReviewStatus.CHANGES_REQUESTED:
            submission.status = Submission.SubmissionStatus.CHANGES_REQUESTED
        elif status == SubmissionReview.ReviewStatus.APPROVED:
            submission.status = Submission.SubmissionStatus.APPROVED
            submission.final_score = score
            submission.reviewed_at = timezone.now()
        elif status == SubmissionReview.ReviewStatus.REJECTED:
            submission.status = Submission.SubmissionStatus.REJECTED
            submission.final_score = score
            submission.reviewed_at = timezone.now()

        submission.save()

        
        from src.backend.submissions.application.event_emitters import (
            emit_submission_reviewed,
            emit_submission_approved,
            emit_submission_changes_requested,
            emit_submission_rejected,
        )

        
        transaction.on_commit(lambda: emit_submission_reviewed(review))

        
        if status == SubmissionReview.ReviewStatus.APPROVED:
            transaction.on_commit(lambda: emit_submission_approved(review))
        elif status == SubmissionReview.ReviewStatus.CHANGES_REQUESTED:
            transaction.on_commit(lambda: emit_submission_changes_requested(review))
        elif status == SubmissionReview.ReviewStatus.REJECTED:
            transaction.on_commit(lambda: emit_submission_rejected(review))

        return review

    @staticmethod
    def get_pending_reviews(mentor_id: UUID = None, limit: int = 50):
        """
        Get submissions waiting for review.

        Filters:
        - status = submitted OR under_review
        """
        submissions = Submission.objects.filter(
            status__in=[
                Submission.SubmissionStatus.SUBMITTED,
                Submission.SubmissionStatus.UNDER_REVIEW
            ]
        ).select_related('assignment').order_by('last_submitted_at')[:limit]

        

        return submissions
