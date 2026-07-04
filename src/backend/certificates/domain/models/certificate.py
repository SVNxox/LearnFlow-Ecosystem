"""
Certificate model — Aggregate Root
"""

import uuid
from decimal import Decimal

from django.db import models
from django.conf import settings


class Certificate(models.Model):
    """
    Certificate issued to a student upon course completion.

    This is a snapshot of data at issuance time — do NOT auto-update.
    """

    STATUSES = [
        ('pending', 'Pending'),      
        ('issued', 'Issued'),        
        ('revoked', 'Revoked'),      
    ]

    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='certificates',
        help_text="Student who received the certificate"
    )

    enrollment_id = models.UUIDField(
        help_text="Enrollment ID (soft reference)"
    )

    course_id = models.UUIDField(
        help_text="Course ID (denormalized)"
    )

    template = models.ForeignKey(
        'certificates.CertificateTemplate',
        on_delete=models.PROTECT,
        related_name='certificates',
        help_text="Template used for this certificate"
    )

    
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique certificate number (e.g., LF-2026-8AF3D2)"
    )

    verification_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Public verification code (same as certificate_number)"
    )

    
    student_full_name_snapshot = models.CharField(
        max_length=255,
        help_text="Student name at issuance time"
    )

    course_name_snapshot = models.CharField(
        max_length=255,
        help_text="Course name at issuance time"
    )

    course_description_snapshot = models.TextField(
        null=True,
        blank=True,
        help_text="Course description at issuance time"
    )

    final_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final course score (percentage)"
    )

    completion_date = models.DateField(
        help_text="Date when course was completed"
    )

    issued_at = models.DateTimeField(
        help_text="When the certificate was issued"
    )

    
    pdf_url = models.TextField(
        null=True,
        blank=True,
        help_text="S3 URL to generated PDF"
    )

    pdf_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When PDF was generated"
    )

    
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='pending',
        help_text="Certificate status"
    )

    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the certificate was revoked"
    )

    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_certificates',
        help_text="Admin who revoked the certificate"
    )

    revoked_reason = models.TextField(
        null=True,
        blank=True,
        help_text="Reason for revocation"
    )

    
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata"
    )

    class Meta:
        db_table = 'certificates_certificate'
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['user', 'status'], name='idx_cert_user_status'),
            models.Index(fields=['enrollment_id'], name='idx_cert_enrollment'),
            models.Index(fields=['course_id', 'issued_at'], name='idx_cert_course'),
            models.Index(fields=['status', 'issued_at'], name='idx_cert_status'),
            models.Index(fields=['verification_code'], name='idx_cert_verification'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['pending', 'issued', 'revoked']),
                name='chk_cert_status'
            ),
        ]

    def __str__(self):
        return f"{self.certificate_number} - {self.student_full_name_snapshot}"

    @property
    def is_valid(self) -> bool:
        """Check if certificate is currently valid."""
        return self.status == 'issued'

    @property
    def is_revoked(self) -> bool:
        """Check if certificate is revoked."""
        return self.status == 'revoked'

    @property
    def is_pending(self) -> bool:
        """Check if PDF generation is pending."""
        return self.status == 'pending'

    def can_be_revoked(self) -> bool:
        """Check if certificate can be revoked."""
        return self.status == 'issued'
