"""
Submit Revision Command

Student submits work (new revision).
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from src.backend.submissions.domain.models import Submission, SubmissionRevision
from src.backend.submissions.domain.services.submission_service import SubmissionService


@dataclass
class SubmitRevisionCommand:
    """
    Submit new revision for submission.

    Called by: Student when submitting work

    Payload examples:
    - github_repository: {"github_url": "...", "live_url": "...", "notes": "..."}
    - file_upload: {"file_id": "uuid", "file_name": "...", "file_size": 123}
    - text_answer: {"answer": "..."}
    - external_link: {"url": "...", "platform": "figma", "notes": "..."}
    """
    submission_id: UUID
    student_id: UUID  
    submission_type: str  
    payload: dict
    notes: Optional[str] = ""


class SubmitRevisionHandler:
    """
    Handler for SubmitRevisionCommand.

    Validation:
    - Submission must be in draft or changes_requested status
    - submission_type must be in assignment.submission_types_allowed
    - Student must own the submission
    - Deadline must not be passed (if set)

    Events emitted:
    - SubmissionSubmitted (Signal) → Mentorship work queue
    """

    @staticmethod
    @transaction.atomic
    def handle(command: SubmitRevisionCommand) -> SubmissionRevision:
        submission = Submission.objects.select_related('assignment').get(id=command.submission_id)

        
        if submission.student_id != command.student_id:
            raise PermissionError("You don't own this submission")

        
        if submission.status not in [
            Submission.SubmissionStatus.DRAFT,
            Submission.SubmissionStatus.CHANGES_REQUESTED
        ]:
            raise ValueError(f"Cannot submit from status {submission.status}")

        
        if submission.deadline and timezone.now() > submission.deadline:
            raise ValueError("Deadline has passed")

        
        if command.submission_type not in submission.assignment.submission_types_allowed:
            raise ValueError(
                f"submission_type '{command.submission_type}' not allowed. "
                f"Allowed: {submission.assignment.submission_types_allowed}"
            )

        
        SubmitRevisionHandler._validate_payload(command.submission_type, command.payload)

        
        revision = SubmissionService.submit_revision(
            submission_id=command.submission_id,
            submission_type=command.submission_type,
            payload=command.payload,
            notes=command.notes or ""
        )

        
        transaction.on_commit(lambda: _emit_submission_submitted_event(revision))

        return revision

    @staticmethod
    def _validate_payload(submission_type: str, payload: dict):
        """Validate payload structure based on submission_type."""
        if submission_type == 'github_repository':
            if 'github_url' not in payload:
                raise ValueError("github_url is required in payload")

        elif submission_type == 'file_upload':
            required = ['file_id', 'file_name', 'file_size', 'mime_type']
            for field in required:
                if field not in payload:
                    raise ValueError(f"{field} is required in payload for file_upload")

        elif submission_type == 'text_answer':
            if 'answer' not in payload:
                raise ValueError("answer is required in payload")

        elif submission_type == 'external_link':
            if 'url' not in payload:
                raise ValueError("url is required in payload")
        else:
            raise ValueError(f"Unknown submission_type: {submission_type}")


def _emit_submission_submitted_event(revision: SubmissionRevision):
    """
    Emit SubmissionSubmitted event.

    TODO: Implement after event handlers task.
    """
    pass
