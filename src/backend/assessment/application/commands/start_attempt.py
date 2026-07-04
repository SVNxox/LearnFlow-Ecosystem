"""
Start Assessment Attempt Command

Creates a new attempt for a student to take an assessment.
"""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from src.backend.assessment.domain.models import (
    ModuleAssessment,
    AssessmentAttempt,
    AssessmentResponse,
)


@dataclass
class StartAttemptCommand:
    """
    Command to start a new assessment attempt.

    Validates:
    - Assessment is published
    - Student hasn't exceeded max_attempts
    - Enrollment is valid
    """
    enrollment_id: UUID
    assessment_id: UUID
    user_id: UUID

    @transaction.atomic
    def execute(self) -> AssessmentAttempt:
        """
        Create new attempt.

        Returns:
            AssessmentAttempt instance

        Raises:
            ValueError: if validation fails
        """
        assessment = ModuleAssessment.objects.get(id=self.assessment_id)

        if not assessment.is_published:
            raise ValueError("Assessment is not published")

        attempt_count = AssessmentAttempt.objects.filter(
            enrollment_id=self.enrollment_id,
            assessment=assessment
        ).count()

        if assessment.max_attempts and attempt_count >= assessment.max_attempts:
            raise ValueError(f"Maximum attempts ({assessment.max_attempts}) reached")

        attempt_number = attempt_count + 1

        expires_at = None
        if assessment.time_limit_minutes:
            expires_at = timezone.now() + timedelta(minutes=assessment.time_limit_minutes)

        attempt = AssessmentAttempt.objects.create(
            enrollment_id=self.enrollment_id,
            assessment=assessment,
            user_id=self.user_id,
            attempt_number=attempt_number,
            max_score=assessment.max_score,
            expires_at=expires_at,
            grading_status=AssessmentAttempt.GradingStatus.PENDING
        )

        items = assessment.items.all()
        for item in items:
            AssessmentResponse.objects.create(
                attempt=attempt,
                item=item
            )

        return attempt
