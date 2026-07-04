"""
Progress Domain Event Handlers

Handles events from other domains (cross-domain integration).

Events consumed:
1. StudentEnrolled (Outbox) — from Enrollment Domain
2. SubmissionApproved (Outbox) — from Submissions Domain
3. AssessmentPassed (Signal) — from Assessment Domain
4. AttendanceMarked (Signal) — from Mentorship Domain
5. LessonPublished (Signal) — from Learning Domain
"""
from uuid import UUID
import logging

from django.dispatch import receiver
from django.db import transaction

from src.backend.progress.domain.services import (
    ProgressInitializationService,
    LessonCompletionService,
    CompletionCascadeService,
)

logger = logging.getLogger(__name__)






def handle_student_enrolled_outbox(payload: dict):
    """
    Handle StudentEnrolled event from Enrollment Domain.

    This is a CRITICAL event (Outbox Pattern - ADR-029).
    Creates aggregate root (CourseProgress).

    Called by: shared.tasks.process_outbox_events

    Payload:
        {
            'enrollment_id': str(UUID),
            'user_id': str(UUID),
            'course_id': str(UUID),
            'delivery_format': 'online' | 'offline',
            'occurred_at': ISO timestamp
        }
    """
    enrollment_id = UUID(payload['enrollment_id'])
    user_id = UUID(payload['user_id'])
    course_id = UUID(payload['course_id'])
    delivery_format = payload['delivery_format']

    try:
        
        is_sequential = True  

        ProgressInitializationService.initialize_progress(
            enrollment_id=enrollment_id,
            user_id=user_id,
            course_id=course_id,
            delivery_format=delivery_format,
            is_sequential=is_sequential,
        )

        logger.info(
            f"Progress initialized for enrollment {enrollment_id}",
            extra={
                'enrollment_id': str(enrollment_id),
                'course_id': str(course_id),
                'delivery_format': delivery_format,
            }
        )
    except Exception as e:
        logger.error(
            f"Failed to initialize progress for enrollment {enrollment_id}: {e}",
            exc_info=True,
            extra={'enrollment_id': str(enrollment_id)}
        )
        raise  


def handle_submission_approved_outbox(payload: dict):
    """
    Handle SubmissionApproved event from Submissions Domain.

    This is a CRITICAL event (Outbox Pattern - ADR-029).
    Updates homework_submitted flag.

    Payload:
        {
            'submission_id': str(UUID),
            'enrollment_id': str(UUID),
            'assignment_id': str(UUID),
            'lesson_id': str(UUID),
            'occurred_at': ISO timestamp
        }
    """
    enrollment_id = UUID(payload['enrollment_id'])
    lesson_id = UUID(payload['lesson_id'])

    try:
        result = LessonCompletionService.mark_homework_submitted(
            enrollment_id=enrollment_id,
            lesson_id=lesson_id,
        )

        logger.info(
            f"Homework submitted for lesson {lesson_id}, completed={result['lesson_completed']}",
            extra={
                'enrollment_id': str(enrollment_id),
                'lesson_id': str(lesson_id),
                'lesson_completed': result['lesson_completed'],
            }
        )
    except Exception as e:
        logger.error(
            f"Failed to mark homework submitted: {e}",
            exc_info=True,
            extra={
                'enrollment_id': str(enrollment_id),
                'lesson_id': str(lesson_id),
            }
        )
        raise




































from src.backend.assessment.domain.events import assessment_passed

@receiver(assessment_passed)
def handle_assessment_passed(sender, enrollment_id, module_id, assessment_id, **kwargs):
    """
    Handle assessment_passed event from Assessment Domain.

    Marks assessment_passed flag and checks module completion.

    Args:
        enrollment_id: UUID object (already a UUID, not a string)
        module_id: UUID object (already a UUID, not a string)
    """
    try:
        CompletionCascadeService.mark_assessment_passed(
            enrollment_id=enrollment_id,
            module_id=module_id,
        )

        logger.info(
            f"Assessment passed for module {module_id}",
            extra={
                'enrollment_id': str(enrollment_id),
                'module_id': str(module_id),
            }
        )
    except Exception as e:
        logger.error(
            f"Failed to mark assessment passed: {e}",
            exc_info=True,
            extra={
                'enrollment_id': str(enrollment_id),
                'module_id': str(module_id),
            }
        )
        

































PROGRESS_EVENT_HANDLERS = {
    'StudentEnrolled': handle_student_enrolled_outbox,
    'SubmissionApproved': handle_submission_approved_outbox,
}
