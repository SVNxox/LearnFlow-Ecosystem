"""
Finalize Attempt Command

Finalizes an assessment attempt after all responses are submitted.
"""
from dataclasses import dataclass
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from src.backend.assessment.domain.models import AssessmentAttempt


@dataclass
class FinalizeAttemptCommand:
    """
    Command to finalize assessment attempt.

    Called when:
    - Student submits all responses (manual finalization)
    - Time limit expires (auto-finalization)

    Sets submitted_at timestamp and triggers completion check.
    """
    attempt_id: UUID

    @transaction.atomic
    def execute(self) -> AssessmentAttempt:
        """
        Mark attempt as submitted and trigger grading completion check.

        Returns:
            AssessmentAttempt instance

        Raises:
            ValueError: if validation fails
        """
        attempt = AssessmentAttempt.objects.select_for_update().get(id=self.attempt_id)

        if attempt.submitted_at:
            raise ValueError("Attempt already submitted")

        total_items = attempt.assessment.items.count()
        submitted_count = attempt.responses.exclude(
            selected_option_ids=[],
            text_response='',
            submitted_code='',
            submission_id__isnull=True
        ).count()

        if submitted_count < total_items:
            raise ValueError(f"Not all items answered ({submitted_count}/{total_items})")

        attempt.submitted_at = timezone.now()
        attempt.save()

        from src.backend.assessment.domain.services import GradingService
        GradingService.check_attempt_completion(attempt.id)

        attempt.refresh_from_db()

        return attempt
