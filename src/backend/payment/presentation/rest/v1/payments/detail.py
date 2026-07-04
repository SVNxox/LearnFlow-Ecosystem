"""
Payment detail endpoint — GET /api/v1/payment/payments/{id}/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.payment.application.queries.payment_detail import (
    PaymentDetailQuery,
    PaymentDetailHandler,
)
from src.backend.payment.presentation.rest.v1.payments.serializers import PaymentDetailSerializer


class PaymentDetailView(APIView):
    """Retrieve payment details."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PaymentDetailSerializer},
        tags=['Payment — Payments'],
        operation_id='get_payment',
        description='Retrieve payment details by ID',
    )
    def get(self, request: Request, payment_id: str) -> Response:
        """Get payment details."""
        query = PaymentDetailQuery(
            payment_id=UUID(payment_id),
            user_id=request.user.id,
        )

        handler = PaymentDetailHandler()
        payment = handler.handle(query)

        serializer = PaymentDetailSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
