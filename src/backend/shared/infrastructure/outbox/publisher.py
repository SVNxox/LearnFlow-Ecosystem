"""
Shared Infrastructure — Outbox Pattern Publisher.

Publishes domain events to DomainEventOutbox for guaranteed delivery.
Events are processed asynchronously by Celery Beat.
"""
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


def publish_to_outbox(event_type: str, aggregate_id: UUID, payload: dict):
    """
    Publish domain event to Outbox for guaranteed delivery.

    This function is called within a database transaction. The event
    is stored in the same transaction as the business operation.

    Args:
        event_type: Name of the event (e.g., 'StudentEnrolled')
        aggregate_id: ID of the aggregate root
        payload: Event data as dict (must be JSON-serializable)

    Example:
        with transaction.atomic():
            enrollment = CourseEnrollment.objects.create(...)
            publish_to_outbox(
                event_type='StudentEnrolled',
                aggregate_id=enrollment.id,
                payload={
                    'enrollment_id': str(enrollment.id),
                    'user_id': str(enrollment.user_id),
                    'course_id': str(enrollment.course_id),
                    'delivery_format': enrollment.delivery_format,
                    'occurred_at': timezone.now().isoformat(),
                }
            )
    """
    from src.backend.audit.models import DomainEventOutbox

    DomainEventOutbox.objects.create(
        event_type=event_type,
        aggregate_id=aggregate_id,
        payload=payload,
    )

    logger.debug(
        f"Event published to outbox: {event_type}",
        extra={
            'event_type': event_type,
            'aggregate_id': str(aggregate_id),
        }
    )
