"""
Payment creation endpoint — POST /api/v1/payment/payments/create/
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.payment.application.commands.create_payment import (
    CreatePaymentCommand,
    CreatePaymentHandler,
)
from src.backend.payment.presentation.rest.v1.payments.serializers import (
    PaymentCreateSerializer,
    PaymentDetailSerializer,
)


class CreatePaymentView(APIView):
    """Create a new payment."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PaymentCreateSerializer,
        responses={201: PaymentDetailSerializer},
        tags=['Payment — Payments'],
        operation_id='create_payment',
        description='Create a new payment for an enrollment or course purchase',
    )
    def post(self, request: Request) -> Response:
        """Create payment."""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        command = CreatePaymentCommand(
            user_id=request.user.id,
            enrollment_id=data.get('enrollment_id'),
            course_id=data.get('course_id'),
            amount=data['amount'],
            currency=data.get('currency', 'UZS'),
            provider=data.get('provider', 'stripe'),
            payment_method=data.get('payment_method', 'card'),  
            idempotency_key=data.get('idempotency_key'),
            metadata=data.get('metadata', {}),
        )

        handler = CreatePaymentHandler()
        payment = handler.handle(command)

        response_serializer = PaymentDetailSerializer(payment)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )