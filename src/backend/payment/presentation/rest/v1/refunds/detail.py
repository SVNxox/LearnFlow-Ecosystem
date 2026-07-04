"""
Refund detail endpoint — GET /api/v1/payment/refunds/{id}/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.payment.domain.models import Refund
from src.backend.payment.presentation.rest.v1.payments.serializers import RefundDetailSerializer


class RefundDetailView(APIView):
    """Retrieve refund details."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: RefundDetailSerializer},
        tags=['Payment — Refunds'],
        operation_id='get_refund',
        description='Retrieve refund details by ID',
    )
    def get(self, request: Request, refund_id: str) -> Response:
        """Get refund details."""
        try:
            refund = Refund.objects.select_related('payment').get(
                id=UUID(refund_id)
            )
        except Refund.DoesNotExist:
            return Response(
                {'detail': 'Refund not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        
        if not request.user.is_staff:
            if refund.payment.user_id != request.user.id:
                return Response(
                    {'detail': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = RefundDetailSerializer(refund)
        return Response(serializer.data, status=status.HTTP_200_OK)
