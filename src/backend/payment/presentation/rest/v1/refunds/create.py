"""
Refund creation endpoint — POST /api/v1/payment/payments/{id}/refund/
"""

from uuid import UUID

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from src.backend.payment.application.commands.create_refund import (
    CreateRefundCommand,
    CreateRefundHandler,
)
from src.backend.payment.presentation.rest.v1.payments.serializers import (
    RefundCreateSerializer,
    RefundDetailSerializer,
)


class CreateRefundView(APIView):
    """Create a refund for a payment."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        request=RefundCreateSerializer,
        responses={201: RefundDetailSerializer},
        tags=['Payment — Refunds'],
        operation_id='create_refund',
        description='Create a refund for an existing payment (admin only)',
    )
    def post(self, request: Request, payment_id: str) -> Response:
        """Create refund."""
        serializer = RefundCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        command = CreateRefundCommand(
            payment_id=UUID(payment_id),
            amount=serializer.validated_data['amount'],
            reason=serializer.validated_data['reason'],
            created_by_id=request.user.id,
            metadata=serializer.validated_data.get('metadata', {}),
        )

        handler = CreateRefundHandler()
        refund = handler.handle(command)

        response_serializer = RefundDetailSerializer(refund)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
