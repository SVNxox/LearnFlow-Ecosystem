"""
PaymentDetail serializer — GET /api/v1/payment/payments/{id}/
"""

from rest_framework import serializers

from src.backend.payment.domain.models import Payment


class PaymentDetailSerializer(serializers.ModelSerializer):
    """Serializer for payment detail view."""

    user_id = serializers.UUIDField(source='user.id', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    is_terminal = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id',
            'user_id',
            'user_email',
            'enrollment_id',
            'amount',
            'currency',
            'provider',
            'provider_payment_id',
            'status',
            'payment_method',
            'card_last4',
            'card_brand',
            'idempotency_key',
            'failure_code',
            'failure_message',
            'succeeded_at',
            'failed_at',
            'refunded_at',
            'is_terminal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_is_terminal(self, obj: Payment) -> bool:
        """Check if payment is in terminal state."""
        return obj.is_terminal()
