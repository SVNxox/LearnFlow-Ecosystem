"""
Payment detail serializer
"""

from rest_framework import serializers
from src.backend.payment.domain.models import Payment


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment details."""

    
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    
    currency = serializers.CharField(
        max_length=3,
        read_only=True
    )

    
    refunded_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        required=False
    )

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'enrollment_id',
            'user_id',
            'amount',
            'currency',
            'refunded_amount',
            'status',
            'status_display',
            'payment_method',
            'provider',
            'provider_payment_id',
            'idempotency_key',
            'failure_code',
            'failure_message',
            'metadata',
            'created_at',
            'updated_at',
            'succeeded_at',
            'failed_at',
        ]
        read_only_fields = fields