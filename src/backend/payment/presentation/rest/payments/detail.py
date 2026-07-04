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

from src.backend.payment.application.queries import (
    PaymentDetailQuery,
    PaymentDetailHandler,
)
from src.backend.payment.presentation.rest.payments.serializers import (
    PaymentDetailSerializer,
)


class PaymentDetailView(APIView):
    """
    Payment detail — Get payment by ID.

    GET /api/v1/payment/payments/{id}/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: PaymentDetailSerializer},
        tags=['Payment'],
        operation_id='payment_detail',
        summary='Get payment details',
        description='Get payment details by ID',
    )
    def get(self, request: Request, payment_id: str) -> Response:
        """Get payment detail."""
        try:
            
            query = PaymentDetailQuery(
                payment_id=UUID(payment_id),
                user_id=request.user.id
            )

            
            payment = PaymentDetailHandler.handle(query)

        except PermissionError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        
        serializer = PaymentDetailSerializer(payment)
        return Response(serializer.data)
