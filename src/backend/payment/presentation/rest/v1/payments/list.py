"""
Payment list endpoint — GET /api/v1/payment/payments/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from src.backend.payment.application.queries.my_payments import (
    MyPaymentsQuery,
    MyPaymentsHandler,
)
from src.backend.payment.presentation.rest.v1.payments.serializers import PaymentListSerializer


class PaymentListView(APIView):
    """List user's payments."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PaymentListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='enrollment_id',
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter by enrollment ID'
            ),
        ],
        tags=['Payment — Payments'],
        operation_id='list_payments',
        description='List all payments for the authenticated user',
    )
    def get(self, request: Request) -> Response:
        """List payments."""
        enrollment_id = request.query_params.get('enrollment_id')

        query = MyPaymentsQuery(
            user_id=request.user.id,
            enrollment_id=enrollment_id,
        )

        handler = MyPaymentsQueryHandler()
        payments = handler.handle(query)

        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
