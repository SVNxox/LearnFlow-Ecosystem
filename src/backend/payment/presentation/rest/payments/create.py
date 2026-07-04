"""
Create payment endpoint — POST /api/v1/payment/payments/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.payment.application.commands import (
    CreatePaymentCommand,
    CreatePaymentHandler,
)
from src.backend.payment.presentation.rest.payments.serializers import (
    PaymentCreateSerializer,
    PaymentDetailSerializer,
)


class CreatePaymentView(APIView):
    """
    Create payment — Student creates payment for enrollment.

    POST /api/v1/payment/payments/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaymentCreateSerializer,
        responses={201: PaymentDetailSerializer},
        tags=['Payment'],
        operation_id='payment_create',
        summary='Create payment',
        description='Create payment for enrollment',
    )
    def post(self, request: Request) -> Response:
        """Create payment."""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        command = CreatePaymentCommand(
            user_id=request.user.id,
            enrollment_id=serializer.validated_data['enrollment_id'],
            amount=serializer.validated_data['amount'],
            currency=serializer.validated_data.get('currency', 'USD'),
            provider=serializer.validated_data.get('provider', 'stripe'),
            metadata=serializer.validated_data.get('metadata', {}),
        )

        
        try:
            payment = CreatePaymentHandler.handle(command)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        response_serializer = PaymentDetailSerializer(payment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
