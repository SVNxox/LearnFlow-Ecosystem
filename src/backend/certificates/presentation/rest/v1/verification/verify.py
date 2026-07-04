"""
Public certificate verification endpoint — GET /api/v1/certificates/verify/{code}/
"""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.certificates.application.queries import (
    VerifyCertificateQuery,
    VerifyCertificateQueryHandler,
)
from src.backend.certificates.presentation.rest.v1.certificates.serializers import (
    VerifyCertificateSerializer,
)


class VerifyCertificateView(APIView):
    """
    Public certificate verification endpoint.

    No authentication required — anyone can verify a certificate.
    """

    permission_classes = []  
    authentication_classes = []

    @extend_schema(
        responses={200: VerifyCertificateSerializer},
        tags=['Certificates — Verification'],
        operation_id='verify_certificate',
        description='Verify a certificate by its verification code (public endpoint)',
    )
    def get(self, request: Request, verification_code: str) -> Response:
        """Verify certificate by code."""

        query = VerifyCertificateQuery(verification_code=verification_code)

        handler = VerifyCertificateQueryHandler()
        result = handler.handle(query)

        if not result:
            return Response(
                {
                    'valid': False,
                    'status': 'not_found',
                    'message': 'Certificate not found',
                },
                status=status.HTTP_404_NOT_FOUND
            )

        
        if result.get('valid'):
            from src.backend.certificates.domain.models import Certificate, CertificateAuditLog
            certificate = Certificate.objects.get(
                verification_code=verification_code
            )
            CertificateAuditLog.objects.create(
                certificate=certificate,
                action='verified',
                actor=None,  
                details={'user_agent': request.META.get('HTTP_USER_AGENT')},
                ip_address=request.META.get('REMOTE_ADDR'),
            )

        serializer = VerifyCertificateSerializer(data=result)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
