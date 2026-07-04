"""
Submissions Domain Events

Events emitted by Submissions Domain.
"""
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from uuid import UUID

from django.dispatch import Signal



submission_submitted = Signal()  
submission_approved = Signal()  
submission_changes_requested = Signal()  
submission_rejected = Signal()  



@dataclass
class SubmissionSubmittedEvent:
    """
    Student submitted revision.

    Emitted: after SubmitRevisionCommand
    Consumers: Mentorship (add to work queue)
    """
    submission_id: UUID
    revision_id: UUID
    assignment_id: UUID
    enrollment_id: UUID
    student_id: UUID
    revision_number: int
    submission_type: str
    occurred_at: datetime


@dataclass
class SubmissionReviewedEvent:
    """
    Mentor reviewed submission (critical event → Outbox).

    Emitted: after any review command (approve/changes_requested/reject)
    Consumers: Assessment (update response points if assessment-related)
    """
    submission_id: UUID
    revision_id: UUID
    assignment_id: UUID
    assessment_item_id: UUID  
    enrollment_id: UUID
    student_id: UUID
    mentor_id: UUID
    score: Decimal
    max_score: Decimal
    status: str  
    feedback: str
    reviewed_at: datetime


@dataclass
class SubmissionApprovedEvent:
    """
    Submission approved (homework gate).

    Emitted: after ApproveSubmissionCommand
    Consumers: UserProgress (homework gate unlock)
    """
    submission_id: UUID
    assignment_id: UUID
    enrollment_id: UUID
    student_id: UUID
    final_score: Decimal
    occurred_at: datetime


@dataclass
class SubmissionChangesRequestedEvent:
    """
    Mentor requested changes.

    Emitted: after RequestChangesCommand
    Consumers: Notifications (notify student)
    """
    submission_id: UUID
    student_id: UUID
    occurred_at: datetime


@dataclass
class SubmissionRejectedEvent:
    """
    Submission rejected (terminal state).

    Emitted: after RejectSubmissionCommand
    Consumers: Notifications (notify student)
    """
    submission_id: UUID
    student_id: UUID
    occurred_at: datetime
