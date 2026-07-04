"""
List payments endpoint — GET /api/v1/payment/payments/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from src.backend.payment.application.queries import (
    MyPaymentsQuery,
    MyPaymentsHandler,
)
from src.backend.payment.presentation.rest.payments.serializers import (
    PaymentListSerializer,
)


class ListPaymentsView(APIView):
    """
    List my payments — Student's payment history.

    GET /api/v1/payment/payments/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PaymentListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                required=False,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='enrollment_id',
                type=str,
                required=False,
                description='Filter by enrollment'
            ),
        ],
        tags=['Payment'],
        operation_id='payment_list',
        summary='List my payments',
        description='Get list of authenticated user payments',
    )
    def get(self, request: Request) -> Response:
        """List payments."""
        
        query = MyPaymentsQuery(
            user_id=request.user.id,
            status=request.query_params.get('status'),
            enrollment_id=request.query_params.get('enrollment_id'),
        )

        
        payments = MyPaymentsHandler.handle(query)

        
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
