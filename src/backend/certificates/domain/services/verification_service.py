"""
Verification Service — Domain Service for certificate verification
"""

from typing import Optional
from uuid import UUID

from src.backend.certificates.domain.models.certificate import Certificate


class VerificationService:
    """
    Domain service for certificate verification.

    Public endpoint uses this service to verify certificates by code.
    """

    @staticmethod
    def verify_by_code(verification_code: str) -> Optional[dict]:
        """
        Verify a certificate by its verification code.

        Returns certificate details if valid, None if not found or revoked.
        """

        try:
            certificate = Certificate.objects.select_related('user', 'template').get(
                verification_code=verification_code
            )
        except Certificate.DoesNotExist:
            return None

        if certificate.is_revoked:
            return {
                'valid': False,
                'status': 'revoked',
                'certificate_number': certificate.certificate_number,
                'revoked_reason': certificate.revoked_reason,
                'revoked_at': certificate.revoked_at,
            }

        if certificate.is_pending:
            return {
                'valid': False,
                'status': 'pending',
                'certificate_number': certificate.certificate_number,
                'message': 'Certificate is being generated',
            }

        
        return {
            'valid': True,
            'status': 'issued',
            'certificate_number': certificate.certificate_number,
            'verification_code': certificate.verification_code,
            'student_name': certificate.student_full_name_snapshot,
            'course_name': certificate.course_name_snapshot,
            'course_description': certificate.course_description_snapshot,
            'final_score': float(certificate.final_score) if certificate.final_score else None,
            'completion_date': certificate.completion_date.isoformat(),
            'issued_at': certificate.issued_at.isoformat(),
            'issued_by': 'LearnFlow Academy',
        }

    @staticmethod
    def verify_by_id(certificate_id: UUID) -> Optional[dict]:
        """
        Verify a certificate by its ID.

        Used internally (not for public verification).
        """

        try:
            certificate = Certificate.objects.get(id=certificate_id)
        except Certificate.DoesNotExist:
            return None

        return {
            'valid': certificate.is_valid,
            'status': certificate.status,
            'certificate_number': certificate.certificate_number,
            'verification_code': certificate.verification_code,
        }
