"""
Refund serializers
"""

from rest_framework import serializers
from decimal import Decimal

from src.backend.payment.domain.models import Refund


class RefundCreateSerializer(serializers.Serializer):
    """Serializer for creating a refund."""

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        required=True,
        help_text="Refund amount (must be <= payment amount)"
    )

    reason = serializers.CharField(
        max_length=500,
        required=True,
        help_text="Reason for refund"
    )

    metadata = serializers.JSONField(
        required=False,
        default=dict,
        help_text="Additional metadata"
    )


class RefundDetailSerializer(serializers.ModelSerializer):
    """Serializer for refund details."""

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
        model = Refund
        fields = [
            'id',
            'payment_id',
            'amount',
            'currency',
            'status',
            'status_display',
            'reason',
            'reason_details',
            'provider_refund_id',
            'created_at',
            'updated_at',
            'succeeded_at',
            'failed_at',
            'initiated_by_id',
        ]
        read_only_fields = fields
