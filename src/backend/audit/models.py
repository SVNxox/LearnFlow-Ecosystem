"""
Audit Domain Models.

Contains infrastructure models for system-wide concerns:
- DomainEventOutbox: Transactional Outbox Pattern for guaranteed event delivery
"""
import uuid
from django.db import models
from django.utils import timezone


class DomainEventOutbox(models.Model):
    """
    Transactional Outbox for domain events (ADR-029).

    Critical events are stored here atomically with business operations,
    then processed asynchronously by Celery Beat for guaranteed delivery.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        PROCESSED = 'processed', 'Processed'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    
    event_type = models.CharField(max_length=100, db_index=True)
    aggregate_id = models.UUIDField(db_index=True)

    
    payload = models.JSONField()

    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    
    retry_count = models.PositiveSmallIntegerField(default=0)
    max_retries = models.PositiveSmallIntegerField(default=5)
    last_error = models.TextField(null=True, blank=True)

    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'shared_domaineventoutbox'
        verbose_name = 'Domain Event Outbox'
        verbose_name_plural = 'Domain Events Outbox'
        indexes = [
            
            models.Index(
                fields=['status', 'created_at'],
                name='idx_outbox_pending',
            ),
            
            models.Index(
                fields=['aggregate_id', 'created_at'],
                name='idx_outbox_aggregate',
            ),
        ]
        ordering = ['created_at']

    def __str__(self):
        return f"{self.event_type} - {self.aggregate_id} [{self.status}]"

    def mark_processing(self):
        """Mark event as being processed."""
        self.status = self.Status.PROCESSING
        self.save(update_fields=['status'])

    def mark_processed(self):
        """Mark event as successfully processed."""
        self.status = self.Status.PROCESSED
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])

    def mark_failed(self, error_message: str):
        """Mark event as failed and increment retry count."""
        self.status = self.Status.FAILED
        self.retry_count += 1
        self.last_error = error_message
        self.save(update_fields=['status', 'retry_count', 'last_error'])

    def can_retry(self) -> bool:
        """Check if event can be retried."""
        return self.retry_count < self.max_retries
