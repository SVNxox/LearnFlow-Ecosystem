"""
Grading Service

Handles automatic grading for choice-type items.
"""
from decimal import Decimal
from typing import List
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from src.backend.assessment.domain.models import (
    AssessmentItem,
    AssessmentResponse,
    AssessmentOption,
    AssessmentAttempt,
)


class GradingService:
    """
    Grading Service — автоматическая оценка choice items.

    Supports:
    - single_choice: one correct answer
    - multiple_choice: multiple correct answers with partial credit
    """

    @staticmethod
    def grade_single_choice(response: AssessmentResponse) -> Decimal:
        """
        Grade single_choice item.

        Returns max_points if correct, 0 otherwise.
        """
        if not response.selected_option_ids:
            return Decimal('0.00')

        selected_id = response.selected_option_ids[0]

        try:
            option = AssessmentOption.objects.get(
                id=selected_id,
                item=response.item
            )

            if option.is_correct:
                return response.item.max_points
            else:
                return Decimal('0.00')
        except AssessmentOption.DoesNotExist:
            return Decimal('0.00')

    @staticmethod
    def grade_multiple_choice(response: AssessmentResponse) -> Decimal:
        """
        Grade multiple_choice item.

        Partial credit strategy:
        - all_or_nothing: all correct = max_points, else 0
        - proportional: (correct_selected / total_correct) * max_points
        """
        if not response.selected_option_ids:
            return Decimal('0.00')

        all_options = AssessmentOption.objects.filter(item=response.item)
        correct_option_ids = set(
            opt.id for opt in all_options if opt.is_correct
        )
        selected_ids = set(response.selected_option_ids)

        is_perfect = selected_ids == correct_option_ids

        strategy = response.item.partial_credit_strategy

        if strategy == AssessmentItem.PartialCreditStrategy.ALL_OR_NOTHING:
            return response.item.max_points if is_perfect else Decimal('0.00')

        elif strategy == AssessmentItem.PartialCreditStrategy.PROPORTIONAL:
            if is_perfect:
                return response.item.max_points

            correct_selected = selected_ids & correct_option_ids
            incorrect_selected = selected_ids - correct_option_ids

            if not correct_option_ids:
                return Decimal('0.00')

            ratio = Decimal(len(correct_selected) - len(incorrect_selected)) / Decimal(len(correct_option_ids))
            ratio = max(ratio, Decimal('0.00'))

            return (ratio * response.item.max_points).quantize(Decimal('0.01'))

        return Decimal('0.00')

    @staticmethod
    @transaction.atomic
    def auto_grade_response(response_id: UUID):
        """
        Auto-grade a single response.

        Updates:
        - response.auto_points
        - response.is_correct (for choice items)
        - response.is_graded
        - response.final_points (if no mentor override)
        """
        response = AssessmentResponse.objects.select_for_update().get(id=response_id)

        item_type = response.item.type

        if item_type == AssessmentItem.ItemType.SINGLE_CHOICE:
            points = GradingService.grade_single_choice(response)
            response.auto_points = points
            response.is_correct = (points == response.item.max_points)
            response.is_graded = True

        elif item_type == AssessmentItem.ItemType.MULTIPLE_CHOICE:
            points = GradingService.grade_multiple_choice(response)
            response.auto_points = points
            response.is_correct = (points == response.item.max_points)
            response.is_graded = True

        else:
            return

        if response.mentor_points is None:
            response.final_points = response.auto_points

        response.save()

    @staticmethod
    @transaction.atomic
    def check_attempt_completion(attempt_id: UUID):
        """
        Check if all responses are graded.
        If yes, update attempt status and calculate final score.

        Called after:
        - Each auto-graded response
        - Mentor review
        - Coding execution complete
        """
        attempt = AssessmentAttempt.objects.select_for_update().get(id=attempt_id)

        total_items = attempt.assessment.items.count()
        graded_count = attempt.responses.filter(is_graded=True).count()

        if graded_count < total_items:
            has_manual_items = attempt.responses.filter(
                item__mentor_review_required=True,
                is_graded=False
            ).exists()

            if has_manual_items and attempt.grading_status == AssessmentAttempt.GradingStatus.PENDING:
                attempt.grading_status = AssessmentAttempt.GradingStatus.MENTOR_REVIEW
                attempt.save()
            elif not has_manual_items and attempt.grading_status == AssessmentAttempt.GradingStatus.PENDING:
                attempt.grading_status = AssessmentAttempt.GradingStatus.AUTO_GRADED
                attempt.save()
            return

        attempt.calculate_final_score()
        attempt.grading_status = AssessmentAttempt.GradingStatus.FINALIZED
        attempt.graded_at = timezone.now()
        attempt.save()

        from src.backend.assessment.domain.events import assessment_passed, assessment_failed

        if attempt.passed:
            transaction.on_commit(lambda: assessment_passed.send(
                sender=AssessmentAttempt,
                attempt_id=attempt.id,
                enrollment_id=attempt.enrollment_id,
                assessment_id=attempt.assessment_id,
                module_id=attempt.assessment.module_id,
                score_earned=attempt.final_score,
            ))
        else:
            transaction.on_commit(lambda: assessment_failed.send(
                sender=AssessmentAttempt,
                attempt_id=attempt.id,
                enrollment_id=attempt.enrollment_id,
                assessment_id=attempt.assessment_id,
                module_id=attempt.assessment.module_id,
                score_earned=attempt.final_score,
            ))
