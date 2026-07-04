"""
Submissions Event Handlers

Handles events emitted by Submissions Domain.
"""
from django.db import transaction
from django.utils import timezone

from src.backend.submissions.domain.events import (
    submission_submitted,
    submission_approved,
    submission_changes_requested,
    submission_rejected,
    SubmissionSubmittedEvent,
    SubmissionReviewedEvent,
    SubmissionApprovedEvent,
    SubmissionChangesRequestedEvent,
    SubmissionRejectedEvent
)


def emit_submission_submitted(submission, revision):
    """
    Emit SubmissionSubmitted event after student submits revision.

    Signal → Mentorship (add to work queue)
    """
    event = SubmissionSubmittedEvent(
        submission_id=submission.id,
        revision_id=revision.id,
        assignment_id=submission.assignment_id,
        enrollment_id=submission.enrollment_id,
        student_id=submission.student_id,
        revision_number=revision.revision_number,
        submission_type=revision.submission_type,
        occurred_at=timezone.now()
    )

    submission_submitted.send(
        sender=submission.__class__,
        submission_id=event.submission_id,
        revision_id=event.revision_id,
        student_id=event.student_id,
        event=event
    )


def emit_submission_reviewed(review):
    """
    Emit SubmissionReviewed event after mentor reviews (Outbox - critical).

    Outbox → Assessment (update response points if assessment-related)
    """
    from src.backend.shared.infrastructure.outbox.publisher import publish_to_outbox

    submission = review.submission
    assignment = submission.assignment

    event = SubmissionReviewedEvent(
        submission_id=submission.id,
        revision_id=review.revision_id,
        assignment_id=assignment.id,
        assessment_item_id=assignment.assessment_item_id,
        enrollment_id=submission.enrollment_id,
        student_id=submission.student_id,
        mentor_id=review.mentor_id,
        score=review.score,
        max_score=review.max_score,
        status=review.status,
        feedback=review.feedback,
        reviewed_at=review.reviewed_at
    )

    
    if assignment.assessment_item_id:
        publish_to_outbox(
            event_type='SubmissionReviewed',
            aggregate_id=submission.id,
            payload={
                'submission_id': str(event.submission_id),
                'revision_id': str(event.revision_id),
                'assignment_id': str(event.assignment_id),
                'assessment_item_id': str(event.assessment_item_id),
                'enrollment_id': str(event.enrollment_id),
                'student_id': str(event.student_id),
                'mentor_id': str(event.mentor_id),
                'score': str(event.score),
                'max_score': str(event.max_score),
                'status': event.status,
                'feedback': event.feedback,
                'reviewed_at': event.reviewed_at.isoformat()
            }
        )


def emit_submission_approved(review):
    """
    Emit SubmissionApproved event after approval.

    Outbox → UserProgress (homework gate unlock) - CRITICAL EVENT (ADR-029)
    """
    from src.backend.shared.infrastructure.outbox.publisher import publish_to_outbox

    submission = review.submission
    assignment = submission.assignment

    event = SubmissionApprovedEvent(
        submission_id=submission.id,
        assignment_id=submission.assignment_id,
        enrollment_id=submission.enrollment_id,
        student_id=submission.student_id,
        final_score=submission.final_score,
        occurred_at=timezone.now()
    )

    
    publish_to_outbox(
        event_type='SubmissionApproved',
        aggregate_id=submission.id,
        payload={
            'submission_id': str(event.submission_id),
            'assignment_id': str(event.assignment_id),
            'enrollment_id': str(event.enrollment_id),
            'student_id': str(event.student_id),
            'lesson_id': str(assignment.lesson_id) if assignment.lesson_id else None,
            'final_score': str(event.final_score),
            'occurred_at': event.occurred_at.isoformat()
        }
    )


def emit_submission_changes_requested(review):
    """
    Emit SubmissionChangesRequested event.

    Signal → Notifications (notify student)
    """
    submission = review.submission

    event = SubmissionChangesRequestedEvent(
        submission_id=submission.id,
        student_id=submission.student_id,
        occurred_at=timezone.now()
    )

    submission_changes_requested.send(
        sender=submission.__class__,
        submission_id=event.submission_id,
        student_id=event.student_id,
        event=event
    )


def emit_submission_rejected(review):
    """
    Emit SubmissionRejected event.

    Signal → Notifications (notify student)
    """
    submission = review.submission

    event = SubmissionRejectedEvent(
        submission_id=submission.id,
        student_id=submission.student_id,
        occurred_at=timezone.now()
    )

    submission_rejected.send(
        sender=submission.__class__,
        submission_id=event.submission_id,
        student_id=event.student_id,
        event=event
    )
