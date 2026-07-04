"""
Shared Infrastructure — Outbox Event Processor (Celery Task).

Periodically processes pending events from DomainEventOutbox.
Scheduled by Celery Beat every 10 seconds (ADR-029).
"""
import logging
from celery import shared_task
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='shared.process_outbox_events')
def process_outbox_events():
    """
    Process pending events from DomainEventOutbox.

    Called by Celery Beat every 10 seconds.
    Picks up pending events and dispatches them to domain handlers.
    """
    from src.backend.audit.models import DomainEventOutbox

    
    from src.backend.progress.application.handlers.event_handlers import PROGRESS_EVENT_HANDLERS

    
    EVENT_HANDLERS = {
        **PROGRESS_EVENT_HANDLERS,
        
    }

    
    pending_events = DomainEventOutbox.objects.filter(
        status='pending'
    ).order_by('created_at')[:100]  

    processed_count = 0
    failed_count = 0

    for event in pending_events:
        try:
            
            event.mark_processing()

            
            handler = EVENT_HANDLERS.get(event.event_type)
            if not handler:
                logger.error(
                    f"No handler registered for event type: {event.event_type}",
                    extra={'event_id': str(event.id), 'event_type': event.event_type}
                )
                event.mark_failed(f"No handler for event type: {event.event_type}")
                failed_count += 1
                continue

            
            with transaction.atomic():
                handler(event.payload)

            
            event.mark_processed()
            processed_count += 1

            logger.info(
                f"Event processed: {event.event_type}",
                extra={
                    'event_id': str(event.id),
                    'event_type': event.event_type,
                    'aggregate_id': str(event.aggregate_id),
                }
            )

        except Exception as e:
            logger.error(
                f"Failed to process event {event.id}: {e}",
                exc_info=True,
                extra={
                    'event_id': str(event.id),
                    'event_type': event.event_type,
                    'retry_count': event.retry_count,
                }
            )

            error_message = f"{type(e).__name__}: {str(e)}"
            event.mark_failed(error_message)
            failed_count += 1

            
            if event.can_retry():
                event.status = 'pending'  
                event.save(update_fields=['status'])
                logger.info(
                    f"Event will be retried ({event.retry_count}/{event.max_retries})",
                    extra={'event_id': str(event.id)}
                )

    if processed_count > 0 or failed_count > 0:
        logger.info(
            f"Outbox processing complete: {processed_count} processed, {failed_count} failed",
            extra={'processed': processed_count, 'failed': failed_count}
        )

    return {
        'processed': processed_count,
        'failed': failed_count,
    }
