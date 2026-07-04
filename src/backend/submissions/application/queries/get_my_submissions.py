"""
Get My Submissions Query

Student views their submissions.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.backend.submissions.domain.models import Submission


@dataclass
class MySubmissionDTO:
    """Data Transfer Object for student's submission list."""
    id: UUID
    assignment_id: UUID
    assignment_title: str
    assignment_type: str
    assignment_max_score: Decimal
    status: str
    current_revision_number: int
    deadline: Optional[str]
    first_submitted_at: Optional[str]
    last_submitted_at: Optional[str]
    reviewed_at: Optional[str]
    final_score: Optional[Decimal]
    is_overdue: bool


class GetMySubmissionsQuery:
    """
    Get student's submissions.

    Called by: Student
    """

    @staticmethod
    def execute(student_id: UUID, enrollment_id: Optional[UUID] = None) -> list[MySubmissionDTO]:
        """
        Retrieve all submissions for a student.

        Filters:
        - By student_id
        - Optionally by enrollment_id (for specific course)

        Ordered by: last_submitted_at DESC (most recent first)
        """
        queryset = Submission.objects.filter(
            student_id=student_id
        ).select_related('assignment')

        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)

        submissions = queryset.order_by('-last_submitted_at', '-created_at')

        return [
            MySubmissionDTO(
                id=s.id,
                assignment_id=s.assignment.id,
                assignment_title=s.assignment.title,
                assignment_type=s.assignment.type,
                assignment_max_score=s.assignment.max_score,
                status=s.status,
                current_revision_number=s.current_revision_number,
                deadline=s.deadline.isoformat() if s.deadline else None,
                first_submitted_at=s.first_submitted_at.isoformat() if s.first_submitted_at else None,
                last_submitted_at=s.last_submitted_at.isoformat() if s.last_submitted_at else None,
                reviewed_at=s.reviewed_at.isoformat() if s.reviewed_at else None,
                final_score=s.final_score,
                is_overdue=s.is_overdue
            )
            for s in submissions
        ]
