"""
Certificate download endpoint — GET /api/v1/certificates/certificates/{id}/download/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.shortcuts import redirect

from src.backend.certificates.domain.models import Certificate


class CertificateDownloadView(APIView):
    """Download certificate PDF."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={302: None},
        tags=['Certificates — Certificates'],
        operation_id='download_certificate',
        description='Download certificate PDF (redirects to S3 URL)',
    )
    def get(self, request: Request, certificate_id: str) -> Response:
        """Download certificate PDF."""

        try:
            certificate = Certificate.objects.get(id=UUID(certificate_id))
        except Certificate.DoesNotExist:
            return Response(
                {'detail': 'Certificate not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        
        if not request.user.is_staff and certificate.user_id != request.user.id:
            return Response(
                {'detail': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        
        if not certificate.pdf_url:
            return Response(
                {'detail': 'Certificate PDF is not ready yet'},
                status=status.HTTP_202_ACCEPTED
            )

        
        if certificate.is_revoked:
            return Response(
                {'detail': 'Certificate has been revoked'},
                status=status.HTTP_410_GONE
            )

        
        from src.backend.certificates.domain.models import CertificateAuditLog
        CertificateAuditLog.objects.create(
            certificate=certificate,
            action='downloaded',
            actor=request.user,
            details={'user_agent': request.META.get('HTTP_USER_AGENT')},
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        
        return redirect(certificate.pdf_url)
