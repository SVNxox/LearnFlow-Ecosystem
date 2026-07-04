"""
Mentor Review Service

Handles mentor review and score override.
ADR-011: All overrides must be logged with reason.
"""
from decimal import Decimal
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from src.backend.assessment.domain.models import (
    AssessmentResponse,
    AssessmentReviewLog,
)


class MentorReviewService:
    """
    Mentor Review Service — ментор проверяет и может переоценить.

    Used for:
    - text_answer items (manual grading)
    - project items (via Submissions Domain)
    - interview items (manual grading)
    - coding items (mentor can override auto-grade)
    """

    @staticmethod
    @transaction.atomic
    def submit_manual_grade(
        response_id: UUID,
        mentor_id: UUID,
        points: Decimal,
        comment: str
    ):
        """
        Submit manual grade for text_answer/interview/project item.

        Used when item has no auto_points (first-time grading).
        """
        response = AssessmentResponse.objects.select_for_update().get(id=response_id)

        if points < Decimal('0.00') or points > response.item.max_points:
            raise ValueError(f"Points must be between 0 and {response.item.max_points}")

        response.mentor_points = points
        response.final_points = points
        response.reviewed_by_id = mentor_id
        response.reviewed_at = timezone.now()
        response.review_comment = comment
        response.is_graded = True
        response.save()

        AssessmentReviewLog.objects.create(
            response=response,
            attempt_id=response.attempt_id,
            old_score=response.auto_points or Decimal('0.00'),
            new_score=points,
            mentor_id=mentor_id,
            reason=comment
        )

        from src.backend.assessment.domain.services import GradingService
        GradingService.check_attempt_completion(response.attempt_id)

    @staticmethod
    @transaction.atomic
    def override_auto_grade(
        response_id: UUID,
        mentor_id: UUID,
        new_points: Decimal,
        reason: str
    ):
        """
        Override auto-graded response (coding item).

        Requires reason for audit trail.
        """
        response = AssessmentResponse.objects.select_for_update().get(id=response_id)

        if not response.is_graded:
            raise ValueError("Cannot override response that hasn't been graded yet")

        if new_points < Decimal('0.00') or new_points > response.item.max_points:
            raise ValueError(f"Points must be between 0 and {response.item.max_points}")

        if not reason or len(reason.strip()) < 10:
            raise ValueError("Override reason must be at least 10 characters")

        response.apply_mentor_override(
            mentor_id=str(mentor_id),
            new_score=new_points,
            reason=reason
        )

        
        attempt = response.attempt
        attempt.calculate_final_score()
        attempt.save()

    @staticmethod
    def get_pending_reviews(mentor_id: UUID = None, limit: int = 50):
        """
        Get responses waiting for mentor review.

        Filters:
        - grading_status = mentor_review
        - is_graded = False
        - item.mentor_review_required = True
        """
        from src.backend.assessment.domain.models import AssessmentAttempt

        attempts = AssessmentAttempt.objects.filter(
            grading_status=AssessmentAttempt.GradingStatus.MENTOR_REVIEW
        ).select_related('assessment')

        

        pending_responses = []
        for attempt in attempts[:limit]:
            responses = attempt.responses.filter(
                is_graded=False,
                item__mentor_review_required=True
            ).select_related('item')

            for response in responses:
                pending_responses.append({
                    'response_id': response.id,
                    'attempt_id': attempt.id,
                    'user_id': attempt.user_id,
                    'assessment_title': attempt.assessment.title,
                    'item_type': response.item.type,
                    'item_title': response.item.title,
                    'submitted_at': attempt.submitted_at,
                })

        return pending_responses
