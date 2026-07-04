"""
PaymentCreate serializer — POST /api/v1/payment/payments/
"""

from decimal import Decimal

from rest_framework import serializers

from src.backend.payment.domain.models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating payment."""

    enrollment_id = serializers.UUIDField(required=True)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=Decimal('0.01')
    )
    currency = serializers.CharField(
        max_length=3,
        default='USD',
        required=False
    )
    provider = serializers.ChoiceField(
        choices=[
            Payment.Provider.STRIPE,
            Payment.Provider.PAYME,
            Payment.Provider.MANUAL,
        ],
        default=Payment.Provider.STRIPE,
        required=False
    )
    metadata = serializers.JSONField(
        required=False,
        default=dict
    )

    def validate_amount(self, value):
        """Validate amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

    def validate_currency(self, value):
        """Validate currency is ISO 4217 code."""
        if len(value) != 3 or not value.isupper():
            raise serializers.ValidationError("Currency must be 3-letter ISO 4217 code")
        return value
