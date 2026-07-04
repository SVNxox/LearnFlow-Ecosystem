"""
Admin Revoke Certificate API.

Endpoint: POST /api/v1/certificates/admin/certificates/{id}/revoke/
"""

import logging
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from src.backend.certificates.domain.models import Certificate, CertificateAuditLog
from src.backend.learning.utils.permissions import IsAdminOrStaff

logger = logging.getLogger(__name__)


class AdminRevokeCertificateView(APIView):
    """Revoke a certificate."""

    permission_classes = [IsAuthenticated, IsAdminOrStaff]

    def post(self, request: Request, certificate_id: str) -> Response:
        """Revoke a certificate."""
        try:
            cert = get_object_or_404(Certificate, id=certificate_id)

            
            if cert.status == 'revoked':
                return Response(
                    {"detail": "Certificate is already revoked"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if cert.status != 'issued':
                return Response(
                    {"detail": f"Cannot revoke certificate with status '{cert.status}'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            reason = request.data.get('reason', '').strip()
            if not reason:
                return Response(
                    {"detail": "Reason is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            cert.status = 'revoked'
            cert.revoked_at = timezone.now()
            cert.revoked_by = request.user
            cert.revoked_reason = reason
            cert.save(update_fields=['status', 'revoked_at', 'revoked_by', 'revoked_reason', 'updated_at'])

            
            CertificateAuditLog.objects.create(
                certificate=cert,
                action='revoked',
                actor=request.user,
                details={'reason': reason},
                ip_address=request.META.get('REMOTE_ADDR'),
            )

            logger.info(f"Certificate {cert.id} revoked by {request.user.id}: {reason}")

            return Response({
                "id": str(cert.id),
                "status": cert.status,
                "revoked_at": cert.revoked_at.isoformat(),
                "revoked_reason": cert.revoked_reason,
                "revoked_by_id": str(cert.revoked_by_id),
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error revoking certificate: {e}", exc_info=True)
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)