"""
Get Student Attempts Query

Returns list of attempts for a student on a specific assessment.
"""
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from src.backend.assessment.domain.models import AssessmentAttempt


@dataclass
class AttemptSummary:
    """Summary of a single attempt."""
    attempt_id: UUID
    attempt_number: int
    grading_status: str
    started_at: datetime
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    final_score: Optional[Decimal]
    percentage: Optional[Decimal]
    passed: Optional[bool]
    is_expired: bool


@dataclass
class StudentAttemptsResult:
    """List of attempts with metadata."""
    assessment_id: UUID
    assessment_title: str
    user_id: UUID
    attempts: List[AttemptSummary]
    total_attempts: int
    max_attempts: Optional[int]
    can_retry: bool
    best_score: Optional[Decimal]
    best_percentage: Optional[Decimal]


class GetStudentAttemptsQuery:
    """Query to get all attempts for a student on an assessment."""

    def __init__(self, user_id: UUID, assessment_id: UUID):
        self.user_id = user_id
        self.assessment_id = assessment_id

    def execute(self) -> StudentAttemptsResult:
        """
        Execute query.

        Returns:
            StudentAttemptsResult with all attempts
        """
        from src.backend.assessment.domain.models import ModuleAssessment

        assessment = ModuleAssessment.objects.get(id=self.assessment_id)

        attempts_qs = AssessmentAttempt.objects.filter(
            user_id=self.user_id,
            assessment=assessment
        ).order_by('-attempt_number')

        attempts = []
        for attempt in attempts_qs:
            attempts.append(AttemptSummary(
                attempt_id=attempt.id,
                attempt_number=attempt.attempt_number,
                grading_status=attempt.grading_status,
                started_at=attempt.started_at,
                submitted_at=attempt.submitted_at,
                graded_at=attempt.graded_at,
                final_score=attempt.final_score,
                percentage=attempt.percentage,
                passed=attempt.passed,
                is_expired=attempt.is_expired(),
            ))

        total_attempts = len(attempts)
        max_attempts = assessment.max_attempts

        
        can_retry = True
        if max_attempts and total_attempts >= max_attempts:
            can_retry = False

        
        finalized_attempts = [a for a in attempts if a.grading_status == 'finalized']
        best_score = None
        best_percentage = None
        if finalized_attempts:
            best_score = max((a.final_score for a in finalized_attempts if a.final_score), default=None)
            best_percentage = max((a.percentage for a in finalized_attempts if a.percentage), default=None)

        return StudentAttemptsResult(
            assessment_id=assessment.id,
            assessment_title=assessment.title,
            user_id=self.user_id,
            attempts=attempts,
            total_attempts=total_attempts,
            max_attempts=max_attempts,
            can_retry=can_retry,
            best_score=best_score,
            best_percentage=best_percentage,
        )
