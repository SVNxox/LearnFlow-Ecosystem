"""
Certificate Reissue Request model
"""

import uuid

from django.db import models
from django.conf import settings


class CertificateReissueRequest(models.Model):
    """
    Request to reissue a certificate.

    Reasons: name change, course name change, PDF template update, etc.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUSES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    certificate = models.ForeignKey(
        'certificates.Certificate',
        on_delete=models.CASCADE,
        related_name='reissue_requests',
        help_text="Original certificate"
    )

    reason = models.TextField(
        help_text="Reason for reissue request"
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='certificate_reissue_requests',
        help_text="User who requested reissue"
    )

    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the request was made"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='pending',
        help_text="Request status"
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_certificate_reissues',
        help_text="Admin who reviewed the request"
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was reviewed"
    )

    new_certificate = models.OneToOneField(
        'certificates.Certificate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reissued_from_request',
        help_text="New certificate issued (if approved)"
    )

    class Meta:
        db_table = 'certificates_reissuerequest'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['certificate', 'status'], name='idx_reissue_cert_status'),
            models.Index(fields=['status', 'requested_at'], name='idx_reissue_status'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['pending', 'approved', 'rejected']),
                name='chk_reissue_status'
            ),
        ]

    def __str__(self):
        return f"Reissue Request for {self.certificate_id} - {self.status}"
