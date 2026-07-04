"""
Certificate Audit Log model
"""

import uuid

from django.db import models
from django.conf import settings


class CertificateAuditLog(models.Model):
    """
    Audit log for certificate operations.

    Tracks all changes: created, issued, revoked, reissued, downloaded.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    ACTIONS = [
        ('created', 'Created'),
        ('issued', 'Issued'),
        ('revoked', 'Revoked'),
        ('reissued', 'Reissued'),
        ('downloaded', 'Downloaded'),
        ('verified', 'Verified'),
    ]

    certificate = models.ForeignKey(
        'certificates.Certificate',
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text="Certificate this log belongs to"
    )

    action = models.CharField(
        max_length=50,
        choices=ACTIONS,
        help_text="Action performed"
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certificate_actions',
        help_text="User who performed the action"
    )

    details = models.JSONField(
        default=dict,
        help_text="Additional details about the action"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the actor"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed"
    )

    class Meta:
        db_table = 'certificates_auditlog'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['certificate', 'created_at'], name='idx_audit_cert'),
            models.Index(fields=['action', 'created_at'], name='idx_audit_action'),
        ]

    def __str__(self):
        return f"{self.action} - {self.certificate_id} at {self.created_at}"
