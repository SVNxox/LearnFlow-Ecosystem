"""
Payment list serializer
"""

from rest_framework import serializers
from src.backend.payment.domain.models import Payment


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer for payment list view."""

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        source='amount.amount',
        read_only=True
    )

    currency = serializers.CharField(
        source='amount.currency',
        read_only=True
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
            'amount',
            'currency',
            'status',
            'status_display',
            'payment_method',
            'created_at',
            'succeeded_at',
        ]
        read_only_fields = fields
