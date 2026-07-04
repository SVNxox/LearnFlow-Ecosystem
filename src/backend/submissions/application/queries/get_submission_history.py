"""
Get Submission History Query

Timeline of all submission events.
"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.backend.submissions.domain.models import (
    Submission,
    SubmissionRevision,
    SubmissionReview,
    AutoCheck
)


@dataclass
class SubmissionEventDTO:
    """Single event in submission timeline."""
    event_type: str  
    timestamp: str
    revision_number: Optional[int]
    actor_id: Optional[UUID]  
    actor_role: str  
    status: str  
    details: dict  


class GetSubmissionHistoryQuery:
    """
    Get submission timeline.

    Called by: Student (own), Mentor, Staff

    Returns chronological list of all events:
    - Revision submissions
    - Reviews
    - Auto checks
    """

    @staticmethod
    def execute(submission_id: UUID) -> list[SubmissionEventDTO]:
        """
        Build timeline of submission events.

        Events ordered by timestamp ASC (oldest first).
        """
        submission = Submission.objects.get(id=submission_id)
        events = []

        
        revisions = SubmissionRevision.objects.filter(
            submission=submission
        ).order_by('revision_number')

        for revision in revisions:
            
            events.append(
                SubmissionEventDTO(
                    event_type='revision_submitted',
                    timestamp=revision.submitted_at.isoformat(),
                    revision_number=revision.revision_number,
                    actor_id=submission.student_id,
                    actor_role='student',
                    status=Submission.SubmissionStatus.SUBMITTED,
                    details={
                        'submission_type': revision.submission_type,
                        'notes': revision.notes
                    }
                )
            )

            
            auto_checks = AutoCheck.objects.filter(
                revision=revision
            ).order_by('completed_at')

            for check in auto_checks:
                if check.completed_at:
                    events.append(
                        SubmissionEventDTO(
                            event_type='auto_check_completed',
                            timestamp=check.completed_at.isoformat(),
                            revision_number=revision.revision_number,
                            actor_id=None,
                            actor_role='system',
                            status=check.status,
                            details={
                                'score': str(check.score) if check.score else None,
                                'report_summary': check.report.get('summary') if check.report else None
                            }
                        )
                    )

            
            reviews = SubmissionReview.objects.filter(
                revision=revision
            ).order_by('reviewed_at')

            for review in reviews:
                events.append(
                    SubmissionEventDTO(
                        event_type='review_completed',
                        timestamp=review.reviewed_at.isoformat(),
                        revision_number=revision.revision_number,
                        actor_id=review.mentor_id,
                        actor_role='mentor',
                        status=review.status,
                        details={
                            'score': str(review.score),
                            'max_score': str(review.max_score),
                            'feedback_preview': review.feedback[:100] if review.feedback else None
                        }
                    )
                )

        
        events.sort(key=lambda e: e.timestamp)

        return events
