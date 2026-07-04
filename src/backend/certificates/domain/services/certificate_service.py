"""
Certificate Service — Domain Service for certificate generation and management
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from src.backend.certificates.domain.models.certificate import Certificate
from src.backend.certificates.domain.models.template import CertificateTemplate
from src.backend.certificates.domain.value_objects.verification_code import VerificationCode
from src.backend.certificates.domain.events import CertificateIssuedEvent, CertificateRevokedEvent




User = get_user_model()
logger = logging.getLogger(__name__)


class CertificateService:
    """
    Domain service for certificate lifecycle management.

    Responsibilities:
    - Generate certificate (create record)
    - Issue certificate (mark as issued after PDF generation)
    - Revoke certificate
    - Reissue certificate
    """

    @staticmethod
    @transaction.atomic
    def generate_certificate(
        user_id: UUID,
        enrollment_id: UUID,
        course_id: UUID,
        template_id: UUID,
        student_full_name: str,
        course_name: str,
        course_description: Optional[str],
        final_score: Optional[Decimal],
        completion_date: date,
    ) -> Certificate:
        """
        Generate a certificate record (PDF generation happens async).

        Returns Certificate with status='pending'.
        PDF generation will be triggered via Celery task.
        """

        
        existing = Certificate.objects.filter(
            enrollment_id=enrollment_id,
            status__in=['pending', 'issued']
        ).first()

        if existing:
            logger.warning(
                f"Certificate already exists for enrollment {enrollment_id}: {existing.id}"
            )
            return existing

        
        try:
            template = CertificateTemplate.objects.get(id=template_id, is_active=True)
        except CertificateTemplate.DoesNotExist:
            raise ValueError(f"Template {template_id} not found or inactive")

        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User {user_id} not found")

        
        verification_code = VerificationCode.generate(year=completion_date.year)

        
        certificate = Certificate.objects.create(
            user=user,
            enrollment_id=enrollment_id,
            course_id=course_id,
            template=template,
            certificate_number=str(verification_code),
            verification_code=str(verification_code),
            student_full_name_snapshot=student_full_name,
            course_name_snapshot=course_name,
            course_description_snapshot=course_description,
            final_score=final_score,
            completion_date=completion_date,
            issued_at=timezone.now(),
            status='pending',
        )

        logger.info(
            f"Certificate generated: {certificate.id} for enrollment {enrollment_id}"
        )

        
        

        return certificate

    @staticmethod
    @transaction.atomic
    def mark_as_issued(certificate_id: UUID, pdf_url: str) -> Certificate:
        """
        Mark certificate as issued after successful PDF generation.

        This is called by the PDF generation Celery task.
        """

        certificate = Certificate.objects.select_for_update().get(id=certificate_id)

        if certificate.status != 'pending':
            raise ValueError(
                f"Certificate {certificate_id} is not pending (status: {certificate.status})"
            )

        certificate.status = 'issued'
        certificate.pdf_url = pdf_url
        certificate.pdf_generated_at = timezone.now()
        certificate.save(update_fields=['status', 'pdf_url', 'pdf_generated_at', 'updated_at'])

        logger.info(f"Certificate {certificate_id} marked as issued")

        
        
        
        

        logger.info(f"CertificateIssued event would be published (Outbox not implemented yet)")

        return certificate

    @staticmethod
    @transaction.atomic
    def revoke_certificate(
        certificate_id: UUID,
        revoked_by_id: UUID,
        reason: str,
    ) -> Certificate:
        """
        Revoke a certificate.

        Only admin can revoke. Certificate must be in 'issued' status.
        """

        certificate = Certificate.objects.select_for_update().get(id=certificate_id)

        if not certificate.can_be_revoked():
            raise ValueError(
                f"Certificate {certificate_id} cannot be revoked (status: {certificate.status})"
            )

        certificate.status = 'revoked'
        certificate.revoked_at = timezone.now()
        certificate.revoked_by_id = revoked_by_id
        certificate.revoked_reason = reason
        certificate.save(update_fields=[
            'status', 'revoked_at', 'revoked_by_id', 'revoked_reason', 'updated_at'
        ])

        logger.info(f"Certificate {certificate_id} revoked by {revoked_by_id}")

        
        
        
        

        logger.info(f"CertificateRevoked event would be published (Outbox not implemented yet)")

        return certificate
