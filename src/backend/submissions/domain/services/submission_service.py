"""
Submission Service

Handles submission workflow and state transitions.
"""
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from src.backend.submissions.domain.models import (
    Assignment,
    Submission,
    SubmissionRevision,
)


class SubmissionService:
    """
    Submission Service — управление жизненным циклом submission.

    Flow:
    1. Create submission (status=draft)
    2. Submit revision → status=submitted
    3. Mentor reviews → status=under_review
    4. Mentor response → changes_requested OR approved/rejected
    5. If changes_requested → student creates new revision → back to step 2
    """

    @staticmethod
    @transaction.atomic
    def create_submission(
        assignment_id: UUID,
        enrollment_id: UUID,
        student_id: UUID
    ) -> Submission:
        """
        Create new submission for student.

        Called when:
        - Student enrolls in course (for lesson assignments)
        - Student starts assessment attempt (for project items)
        """
        assignment = Assignment.objects.get(id=assignment_id)

        
        existing = Submission.objects.filter(
            assignment=assignment,
            enrollment_id=enrollment_id
        ).first()

        if existing:
            return existing

        
        deadline = None
        if assignment.deadline_offset_days:
            
            
            deadline = timezone.now() + timedelta(days=assignment.deadline_offset_days)

        submission = Submission.objects.create(
            assignment=assignment,
            enrollment_id=enrollment_id,
            student_id=student_id,
            status=Submission.SubmissionStatus.DRAFT,
            deadline=deadline
        )

        return submission

    @staticmethod
    @transaction.atomic
    def submit_revision(
        submission_id: UUID,
        submission_type: str,
        payload: dict,
        notes: str = ""
    ) -> SubmissionRevision:
        """
        Submit new revision.

        Transitions:
        - draft → submitted (first submission)
        - changes_requested → submitted (resubmission)
        """
        submission = Submission.objects.select_for_update().get(id=submission_id)

        
        if submission.status not in [
            Submission.SubmissionStatus.DRAFT,
            Submission.SubmissionStatus.CHANGES_REQUESTED
        ]:
            raise ValueError(f"Cannot submit from status {submission.status}")

        
        revision_number = submission.current_revision_number + 1

        revision = SubmissionRevision.objects.create(
            submission=submission,
            revision_number=revision_number,
            submission_type=submission_type,
            payload=payload,
            notes=notes
        )

        
        submission.current_revision_number = revision_number
        submission.status = Submission.SubmissionStatus.SUBMITTED
        submission.last_submitted_at = timezone.now()

        if not submission.first_submitted_at:
            submission.first_submitted_at = timezone.now()

        submission.save()

        
        

        return revision

    @staticmethod
    @transaction.atomic
    def mark_under_review(submission_id: UUID):
        """
        Mentor starts reviewing.

        Transition: submitted → under_review
        """
        submission = Submission.objects.select_for_update().get(id=submission_id)

        if submission.status != Submission.SubmissionStatus.SUBMITTED:
            raise ValueError(f"Cannot start review from status {submission.status}")

        submission.status = Submission.SubmissionStatus.UNDER_REVIEW
        submission.save()
