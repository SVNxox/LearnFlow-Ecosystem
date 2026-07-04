"""
Event handlers for Enrollment Domain.

Handles incoming events from other domains:
- Payment Domain: PaymentSucceeded, PaymentFailed, RefundIssued
- Progress Domain: CourseCompleted
"""

from django.dispatch import receiver
from django.utils import timezone

from src.backend.enrollment.application.commands import (
    ActivateEnrollmentHandler,
    ActivateEnrollmentCommand,
    SuspendEnrollmentHandler,
    SuspendEnrollmentCommand,
    CompleteEnrollmentHandler,
    CompleteEnrollmentCommand,
    DropEnrollmentHandler,
    DropEnrollmentCommand,
)





def handle_payment_succeeded(payload: dict):
    """
    Handle PaymentSucceeded event from Payment Domain (Outbox).

    Activates pending enrollment.
    """
    enrollment_id = payload.get('enrollment_id')
    payment_id = payload.get('payment_id')

    if not enrollment_id or not payment_id:
        return

    command = ActivateEnrollmentCommand(
        enrollment_id=enrollment_id,
        payment_id=payment_id
    )

    ActivateEnrollmentHandler.handle(command)


def handle_payment_failed(payload: dict):
    """
    Handle PaymentFailed event from Payment Domain (Outbox).

    Suspends enrollment.
    """
    enrollment_id = payload.get('enrollment_id')
    reason = payload.get('reason', 'Payment failed')

    if not enrollment_id:
        return

    command = SuspendEnrollmentCommand(
        enrollment_id=enrollment_id,
        reason=reason
    )

    SuspendEnrollmentHandler.handle(command)


def handle_refund_issued(payload: dict):
    """
    Handle RefundIssued event from Payment Domain (Outbox).

    Drops enrollment (terminal state).
    """
    enrollment_id = payload.get('enrollment_id')
    reason = payload.get('reason', 'Refund issued')

    if not enrollment_id:
        return

    command = DropEnrollmentCommand(
        enrollment_id=enrollment_id,
        reason=reason
    )

    DropEnrollmentHandler.handle(command)





def handle_course_completed(payload: dict):
    """
    Handle CourseCompleted event from Progress Domain (Outbox).

    Marks enrollment as completed.
    """
    enrollment_id = payload.get('enrollment_id')

    if not enrollment_id:
        return

    command = CompleteEnrollmentCommand(
        enrollment_id=enrollment_id
    )

    CompleteEnrollmentHandler.handle(command)





ENROLLMENT_EVENT_HANDLERS = {
    'PaymentSucceeded': handle_payment_succeeded,
    'PaymentFailed': handle_payment_failed,
    'RefundIssued': handle_refund_issued,
    'CourseCompleted': handle_course_completed,
}
