"""
RefundCreate serializer — POST /api/v1/payment/payments/{id}/refund/
"""

from decimal import Decimal

from rest_framework import serializers

from src.backend.payment.domain.models import Refund


class RefundCreateSerializer(serializers.Serializer):
    """Serializer for creating refund."""

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=Decimal('0.01')
    )
    reason = serializers.ChoiceField(
        choices=[
            Refund.Reason.DUPLICATE,
            Refund.Reason.FRAUDULENT,
            Refund.Reason.REQUESTED_BY_CUSTOMER,
            Refund.Reason.COURSE_CANCELLED,
            Refund.Reason.OTHER,
        ],
        required=True
    )
    reason_details = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True
    )

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
