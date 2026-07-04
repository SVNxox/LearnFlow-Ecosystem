"""
Get Submission Detail Query

Retrieve submission with all revisions and reviews.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.backend.submissions.domain.models import (
    Submission,
    SubmissionRevision,
    SubmissionReview,
    SubmissionFile,
    AutoCheck
)


@dataclass
class SubmissionFileDTO:
    """File metadata."""
    id: UUID
    file_key: str
    file_name: str
    file_size: int
    mime_type: str
    scan_status: str
    uploaded_at: str


@dataclass
class AutoCheckDTO:
    """Auto check result."""
    id: UUID
    status: str
    score: Optional[Decimal]
    report: dict
    started_at: Optional[str]
    completed_at: Optional[str]


@dataclass
class ReviewDTO:
    """Review details."""
    id: UUID
    mentor_id: UUID
    score: Decimal
    max_score: Decimal
    feedback: str
    status: str
    reviewed_at: str


@dataclass
class RevisionDTO:
    """Revision with files, auto checks, and review."""
    id: UUID
    revision_number: int
    submission_type: str
    payload: dict
    notes: str
    submitted_at: str
    files: list[SubmissionFileDTO]
    auto_check: Optional[AutoCheckDTO]
    review: Optional[ReviewDTO]


@dataclass
class SubmissionDetailDTO:
    """Complete submission details."""
    id: UUID
    assignment_id: UUID
    assignment_title: str
    assignment_description: str
    assignment_type: str
    assignment_max_score: Decimal
    enrollment_id: UUID
    student_id: UUID
    status: str
    current_revision_number: int
    deadline: Optional[str]
    first_submitted_at: Optional[str]
    last_submitted_at: Optional[str]
    reviewed_at: Optional[str]
    final_score: Optional[Decimal]
    is_overdue: bool
    created_at: str
    updated_at: Optional[str]  
    revisions: list[RevisionDTO]


class GetSubmissionDetailQuery:
    """
    Get complete submission details.

    Called by: Student (own), Mentor, Staff
    """

    @staticmethod
    def execute(submission_id: UUID) -> SubmissionDetailDTO:
        """
        Retrieve submission with full history.

        Includes:
        - All revisions (ordered by revision_number DESC)
        - Files for each revision
        - Auto checks for each revision
        - Reviews for each revision
        """
        submission = Submission.objects.select_related('assignment').get(id=submission_id)

        
        revisions = SubmissionRevision.objects.filter(
            submission=submission
        ).prefetch_related(
            'files',
            'auto_checks',
            'reviews'
        ).order_by('-revision_number')

        revision_dtos = []
        for revision in revisions:
            
            file_dtos = [
                SubmissionFileDTO(
                    id=f.id,
                    file_key=f.file_key,
                    file_name=f.file_name,
                    file_size=f.file_size,
                    mime_type=f.mime_type,
                    scan_status=f.scan_status,
                    uploaded_at=f.uploaded_at.isoformat()
                )
                for f in revision.files.all()
            ]

            
            auto_check = revision.auto_checks.order_by('-started_at').first()
            auto_check_dto = None
            if auto_check:
                auto_check_dto = AutoCheckDTO(
                    id=auto_check.id,
                    status=auto_check.status,
                    score=auto_check.score,
                    report=auto_check.report or {},
                    started_at=auto_check.started_at.isoformat() if auto_check.started_at else None,
                    completed_at=auto_check.completed_at.isoformat() if auto_check.completed_at else None
                )

            
            review = revision.reviews.first()
            review_dto = None
            if review:
                review_dto = ReviewDTO(
                    id=review.id,
                    mentor_id=review.mentor_id,
                    score=review.score,
                    max_score=review.max_score,
                    feedback=review.feedback,
                    status=review.status,
                    reviewed_at=review.reviewed_at.isoformat()
                )

            revision_dtos.append(
                RevisionDTO(
                    id=revision.id,
                    revision_number=revision.revision_number,
                    submission_type=revision.submission_type,
                    payload=revision.payload or {},
                    notes=revision.notes,
                    submitted_at=revision.submitted_at.isoformat(),
                    files=file_dtos,
                    auto_check=auto_check_dto,
                    review=review_dto
                )
            )

        return SubmissionDetailDTO(
            id=submission.id,
            assignment_id=submission.assignment.id,
            assignment_title=submission.assignment.title,
            assignment_description=submission.assignment.description,
            assignment_type=submission.assignment.type,
            assignment_max_score=submission.assignment.max_score,
            enrollment_id=submission.enrollment_id,
            student_id=submission.student_id,
            status=submission.status,
            current_revision_number=submission.current_revision_number,
            deadline=submission.deadline.isoformat() if submission.deadline else None,
            first_submitted_at=submission.first_submitted_at.isoformat() if submission.first_submitted_at else None,
            last_submitted_at=submission.last_submitted_at.isoformat() if submission.last_submitted_at else None,
            reviewed_at=submission.reviewed_at.isoformat() if submission.reviewed_at else None,
            final_score=submission.final_score,
            is_overdue=submission.is_overdue,
            created_at=submission.created_at.isoformat(),
            updated_at=submission.last_submitted_at.isoformat() if submission.last_submitted_at else None,
            revisions=revision_dtos
        )
