"""
Certificate detail endpoint — GET /api/v1/certificates/certificates/{id}/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.certificates.application.queries import (
    CertificateDetailQuery,
    CertificateDetailQueryHandler,
)
from src.backend.certificates.presentation.rest.v1.certificates.serializers import (
    CertificateDetailSerializer,
)


class CertificateDetailView(APIView):
    """Retrieve certificate details."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CertificateDetailSerializer},
        tags=['Certificates — Certificates'],
        operation_id='get_certificate',
        description='Retrieve certificate details by ID',
    )
    def get(self, request: Request, certificate_id: str) -> Response:
        """Get certificate details."""

        query = CertificateDetailQuery(
            certificate_id=UUID(certificate_id),
            user_id=request.user.id if not request.user.is_staff else None,
        )

        handler = CertificateDetailQueryHandler()

        try:
            certificate = handler.handle(query)
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CertificateDetailSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)
