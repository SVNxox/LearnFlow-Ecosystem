


























































"""
Payment create serializer
"""

from rest_framework import serializers
from decimal import Decimal


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment."""

    enrollment_id = serializers.UUIDField(required=False, allow_null=True)
    course_id = serializers.UUIDField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(default='UZS', max_length=3)
    provider = serializers.CharField(default='stripe', max_length=20)
    payment_method = serializers.CharField(default='card', max_length=20)
    idempotency_key = serializers.CharField(required=False, allow_null=True, max_length=255)
    metadata = serializers.JSONField(required=False, default=dict)

    def validate(self, data):
        """Валидация: должен быть либо enrollment_id, либо course_id."""
        if not data.get('enrollment_id') and not data.get('course_id'):
            raise serializers.ValidationError(
                "Either enrollment_id or course_id must be provided"
            )
        return data