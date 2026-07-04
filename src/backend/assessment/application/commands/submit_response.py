"""
Submit Response Command

Submits student's answer to an assessment item.
"""
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from django.db import transaction

from src.backend.assessment.domain.models import (
    AssessmentAttempt,
    AssessmentResponse,
    AssessmentItem,
)
from src.backend.assessment.domain.services import GradingService


@dataclass
class SubmitResponseCommand:
    """
    Command to submit response to an assessment item.

    Auto-grades choice items immediately.
    Coding items are sent to async execution.
    Text/project/interview items wait for mentor review.
    """
    attempt_id: UUID
    item_id: UUID

    selected_option_ids: Optional[List[UUID]] = None
    text_response: Optional[str] = None
    submitted_code: Optional[str] = None
    coding_language: Optional[str] = None

    @transaction.atomic
    def execute(self) -> AssessmentResponse:
        """
        Submit response and trigger grading if applicable.

        Returns:
            AssessmentResponse instance

        Raises:
            ValueError: if validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SubmitResponse: selected_option_ids={self.selected_option_ids}, type={type(self.selected_option_ids)}")

        attempt = AssessmentAttempt.objects.select_for_update().get(id=self.attempt_id)

        if attempt.is_expired():
            raise ValueError("Attempt has expired")

        if attempt.grading_status == AssessmentAttempt.GradingStatus.FINALIZED:
            raise ValueError("Attempt is already finalized")

        response = AssessmentResponse.objects.select_for_update().get(
            attempt=attempt,
            item_id=self.item_id
        )

        if response.is_graded:
            raise ValueError("Response already submitted and graded")

        item_type = response.item.type

        if item_type in [AssessmentItem.ItemType.SINGLE_CHOICE, AssessmentItem.ItemType.MULTIPLE_CHOICE]:
            if not self.selected_option_ids:
                raise ValueError("selected_option_ids required for choice items")
            response.selected_option_ids = list(self.selected_option_ids)  
            logger.info(f"Before save: response.selected_option_ids={response.selected_option_ids}")

        elif item_type in [AssessmentItem.ItemType.TEXT_ANSWER, AssessmentItem.ItemType.INTERVIEW]:
            if not self.text_response:
                raise ValueError("text_response required for text/interview items")
            response.text_response = self.text_response

        elif item_type == AssessmentItem.ItemType.CODING:
            if not self.submitted_code:
                raise ValueError("submitted_code required for coding items")
            response.submitted_code = self.submitted_code
            response.coding_language = self.coding_language or response.item.coding_language

        elif item_type == AssessmentItem.ItemType.PROJECT:
            pass

        response.save(update_fields=['selected_option_ids', 'text_response', 'submitted_code', 'coding_language'])
        response.refresh_from_db()
        logger.info(f"After save+refresh: response.selected_option_ids={response.selected_option_ids}")

        if item_type in [AssessmentItem.ItemType.SINGLE_CHOICE, AssessmentItem.ItemType.MULTIPLE_CHOICE]:
            GradingService.auto_grade_response(response.id)
            GradingService.check_attempt_completion(attempt.id)

        elif item_type == AssessmentItem.ItemType.CODING:
            from src.backend.assessment.infrastructure.tasks import execute_coding_task
            execute_coding_task.delay(response_id=str(response.id))

        elif item_type in [AssessmentItem.ItemType.TEXT_ANSWER, AssessmentItem.ItemType.INTERVIEW, AssessmentItem.ItemType.PROJECT]:
            GradingService.check_attempt_completion(attempt.id)

        return response
