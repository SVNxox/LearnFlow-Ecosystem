"""
My certificates list endpoint — GET /api/v1/certificates/certificates/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from src.backend.certificates.application.queries import (
    MyCertificatesQuery,
    MyCertificatesQueryHandler,
)
from src.backend.certificates.presentation.rest.v1.certificates.serializers import (
    CertificateListSerializer,
)


class MyCertificatesListView(APIView):
    """List user's certificates."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CertificateListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter by status (pending/issued/revoked)'
            ),
        ],
        tags=['Certificates — Certificates'],
        operation_id='list_my_certificates',
        description='List all certificates for the authenticated user',
    )
    def get(self, request: Request) -> Response:
        """List my certificates."""

        query = MyCertificatesQuery(
            user_id=request.user.id,
            status=request.query_params.get('status'),
        )

        handler = MyCertificatesQueryHandler()
        certificates = handler.handle(query)

        serializer = CertificateListSerializer(certificates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
