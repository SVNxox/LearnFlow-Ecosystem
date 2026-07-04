"""
Create refund endpoint — POST /api/v1/payment/payments/{id}/refund/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.payment.application.commands import (
    CreateRefundCommand,
    CreateRefundHandler,
)
from src.backend.payment.domain.models import Payment
from src.backend.payment.presentation.rest.payments.serializers import (
    RefundCreateSerializer,
    PaymentDetailSerializer,
)


class CreateRefundView(APIView):
    """
    Create refund — Admin creates refund for payment.

    POST /api/v1/payment/payments/{id}/refund/

    Requires: Admin permission
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        request=RefundCreateSerializer,
        responses={200: PaymentDetailSerializer},
        tags=['Payment'],
        operation_id='payment_refund',
        summary='Create refund',
        description='Create refund for payment (Admin only)',
    )
    def post(self, request: Request, payment_id: str) -> Response:
        """Create refund."""
        
        serializer = RefundCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            
            payment = Payment.objects.get(id=UUID(payment_id))

            
            command = CreateRefundCommand(
                payment_id=payment.id,
                amount=serializer.validated_data['amount'],
                reason=serializer.validated_data['reason'],
                reason_details=serializer.validated_data.get('reason_details'),
                initiated_by_id=request.user.id,
            )

            
            refund = CreateRefundHandler.handle(command)

            
            payment.refresh_from_db()

        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        response_serializer = PaymentDetailSerializer(payment)
        return Response(response_serializer.data)
